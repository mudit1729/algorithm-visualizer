class GraphRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
    }

    render(step) {
        if (!step.graph_nodes) return;

        const canvas = this.canvas;
        const ctx = this.ctx;

        // Handle HiDPI
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const W = rect.width;
        const H = rect.height;
        ctx.clearRect(0, 0, W, H);

        const nodes = step.graph_nodes;
        const edges = step.graph_edges || [];

        // Layout: nodes have x,y in 0..1 range, map to canvas
        const padding = 60;
        const areaW = W - padding * 2;
        const areaH = H - padding * 2;

        // Build node position map
        const nodeMap = {};
        nodes.forEach(n => {
            nodeMap[n.id] = {
                x: padding + n.x * areaW,
                y: padding + n.y * areaH,
                node: n,
            };
        });

        // Node radius scales with count
        const baseRadius = Math.min(28, Math.max(16, 200 / Math.sqrt(nodes.length)));

        // Colors
        const colors = {
            nodeFill: '#313244',
            nodeStroke: '#585b70',
            nodeText: '#cdd6f4',
            selected: '#f9e2af',
            patched: '#a6e3a1',
            error: '#f38ba8',
            edgeDefault: '#585b70',
            edgeSelected: '#f9e2af',
            edgePatched: '#89b4fa',
            edgeError: '#f38ba8',
        };

        // Edge class color map
        const edgeClassColors = {
            'tree': '#a6e3a1',
            'back': '#f38ba8',
            'cross': '#fab387',
            'forward': '#89dceb',
            'relaxed': '#a6e3a1',
        };

        // Group bounding boxes (draw behind everything)
        const groups = {};
        nodes.forEach(n => {
            if (n.group != null) {
                if (!groups[n.group]) groups[n.group] = [];
                groups[n.group].push(nodeMap[n.id]);
            }
        });

        const groupColors = [
            'rgba(137, 180, 250, 0.08)',
            'rgba(166, 227, 161, 0.08)',
            'rgba(249, 226, 175, 0.08)',
            'rgba(203, 166, 247, 0.08)',
            'rgba(250, 179, 135, 0.08)',
        ];
        const groupBorders = [
            'rgba(137, 180, 250, 0.3)',
            'rgba(166, 227, 161, 0.3)',
            'rgba(249, 226, 175, 0.3)',
            'rgba(203, 166, 247, 0.3)',
            'rgba(250, 179, 135, 0.3)',
        ];

        Object.entries(groups).forEach(([gid, positions], i) => {
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            positions.forEach(p => {
                minX = Math.min(minX, p.x);
                minY = Math.min(minY, p.y);
                maxX = Math.max(maxX, p.x);
                maxY = Math.max(maxY, p.y);
            });
            const pad = baseRadius * 1.5;
            ctx.fillStyle = groupColors[i % groupColors.length];
            ctx.strokeStyle = groupBorders[i % groupBorders.length];
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.roundRect(minX - pad, minY - pad, maxX - minX + pad * 2, maxY - minY + pad * 2, 12);
            ctx.fill();
            ctx.stroke();
        });

        // Draw edges first (behind nodes)
        edges.forEach(e => {
            const src = nodeMap[e.source];
            const tgt = nodeMap[e.target];
            if (!src || !tgt) return;

            let strokeColor = colors.edgeDefault;
            let lineWidth = 1.5;
            if (e.error) {
                strokeColor = colors.edgeError;
                lineWidth = 3;
            } else if (e.selected) {
                strokeColor = colors.edgeSelected;
                lineWidth = 2.5;
            } else if (e.patched) {
                strokeColor = colors.edgePatched;
                lineWidth = 2;
            }

            // Edge class overrides default color
            if (e.edge_class && edgeClassColors[e.edge_class] && !e.error && !e.selected) {
                strokeColor = edgeClassColors[e.edge_class];
                lineWidth = 2.5;
            }

            // Dashed lines for back/cross edges
            if (e.edge_class === 'back' || e.edge_class === 'cross') {
                ctx.setLineDash([6, 4]);
            } else {
                ctx.setLineDash([]);
            }

            ctx.beginPath();
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = lineWidth;

            // Offset start/end to node edge (not center)
            const dx = tgt.x - src.x;
            const dy = tgt.y - src.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 0.1) { ctx.setLineDash([]); return; }

            const ux = dx / dist;
            const uy = dy / dist;
            const sx = src.x + ux * baseRadius;
            const sy = src.y + uy * baseRadius;
            const ex = tgt.x - ux * baseRadius;
            const ey = tgt.y - uy * baseRadius;

            // Bezier curve or straight line
            let mx, my; // midpoint for label placement
            if (e.curve_offset && e.curve_offset !== 0) {
                const midX = (src.x + tgt.x) / 2;
                const midY = (src.y + tgt.y) / 2;
                const cpx = midX + (-uy) * e.curve_offset * dist;
                const cpy = midY + ux * e.curve_offset * dist;
                ctx.moveTo(sx, sy);
                ctx.quadraticCurveTo(cpx, cpy, ex, ey);
                mx = (sx + 2 * cpx + ex) / 4;
                my = (sy + 2 * cpy + ey) / 4;
            } else {
                ctx.moveTo(sx, sy);
                ctx.lineTo(ex, ey);
                mx = (sx + ex) / 2;
                my = (sy + ey) / 2;
            }
            ctx.stroke();
            ctx.setLineDash([]);

            // Arrowhead for directed edges
            const isDirected = e.directed !== undefined ? e.directed : true;
            if (isDirected) {
                const arrowLen = 10;
                const arrowAngle = Math.PI / 7;
                let angle;
                if (e.curve_offset && e.curve_offset !== 0) {
                    // Arrow angle from control point to end
                    const midX = (src.x + tgt.x) / 2;
                    const midY = (src.y + tgt.y) / 2;
                    const cpx = midX + (-uy) * e.curve_offset * dist;
                    const cpy = midY + ux * e.curve_offset * dist;
                    angle = Math.atan2(ey - cpy, ex - cpx);
                } else {
                    angle = Math.atan2(ey - sy, ex - sx);
                }

                ctx.beginPath();
                ctx.fillStyle = strokeColor;
                ctx.moveTo(ex, ey);
                ctx.lineTo(
                    ex - arrowLen * Math.cos(angle - arrowAngle),
                    ey - arrowLen * Math.sin(angle - arrowAngle)
                );
                ctx.lineTo(
                    ex - arrowLen * Math.cos(angle + arrowAngle),
                    ey - arrowLen * Math.sin(angle + arrowAngle)
                );
                ctx.closePath();
                ctx.fill();
            }

            // Weight / label rendering at edge midpoint
            const edgeLabel = e.weight != null ? String(e.weight) : (e.label || '');
            if (edgeLabel) {
                const perpX = -uy * 14;
                const perpY = ux * 14;
                const lx = mx + perpX;
                const ly = my + perpY;
                const fontSize = Math.max(10, Math.floor(baseRadius * 0.45));
                ctx.font = `bold ${fontSize}px -apple-system, sans-serif`;
                const tw = ctx.measureText(edgeLabel).width + 6;
                // Background pill
                ctx.fillStyle = '#1e1e2e';
                ctx.beginPath();
                ctx.roundRect(lx - tw / 2, ly - fontSize * 0.7, tw, fontSize * 1.4, 3);
                ctx.fill();
                // Text
                ctx.fillStyle = '#cdd6f4';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(edgeLabel, lx, ly);
            }
        });

        // Draw nodes
        nodes.forEach(n => {
            const pos = nodeMap[n.id];
            const x = pos.x;
            const y = pos.y;

            // Determine fill color
            let fillColor = colors.nodeFill;
            let strokeColor = colors.nodeStroke;
            let textColor = colors.nodeText;
            let strokeWidth = 2;

            if (n.color) {
                fillColor = n.color;
                textColor = '#1e1e2e';
                strokeColor = n.color;
            }

            if (n.error) {
                fillColor = colors.error;
                strokeColor = colors.error;
                textColor = '#fff';
                strokeWidth = 3;
            } else if (n.selected) {
                strokeColor = colors.selected;
                strokeWidth = 3;
                if (!n.color) fillColor = 'rgba(249, 226, 175, 0.2)';
            } else if (n.patched) {
                fillColor = colors.patched;
                strokeColor = colors.patched;
                textColor = '#1e1e2e';
            }

            // Shadow
            ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
            ctx.shadowBlur = 8;
            ctx.shadowOffsetY = 2;

            // Circle
            ctx.beginPath();
            ctx.arc(x, y, baseRadius, 0, Math.PI * 2);
            ctx.fillStyle = fillColor;
            ctx.fill();
            ctx.shadowColor = 'transparent';

            ctx.lineWidth = strokeWidth;
            ctx.strokeStyle = strokeColor;
            ctx.stroke();

            // Label
            ctx.fillStyle = textColor;
            ctx.font = `bold ${Math.floor(baseRadius * 0.7)}px -apple-system, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(n.label, x, y + 1);

            // Badge (e.g., disc/low for Tarjan)
            if (n.badge) {
                const badgeR = Math.max(8, baseRadius * 0.35);
                const bx = x + baseRadius * 0.75;
                const by = y - baseRadius * 0.75;
                ctx.beginPath();
                ctx.arc(bx, by, badgeR, 0, Math.PI * 2);
                ctx.fillStyle = n.badge_color || '#fab387';
                ctx.fill();
                ctx.strokeStyle = '#1e1e2e';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.fillStyle = '#1e1e2e';
                ctx.font = `bold ${Math.floor(badgeR * 1.0)}px -apple-system, sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(n.badge, bx, by);
            }
        });
    }
}
