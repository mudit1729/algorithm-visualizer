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
        const rect = canvas.parentElement.getBoundingClientRect();
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

            ctx.beginPath();
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = lineWidth;

            // Offset start/end to node edge (not center)
            const dx = tgt.x - src.x;
            const dy = tgt.y - src.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 0.1) return;

            const ux = dx / dist;
            const uy = dy / dist;
            const sx = src.x + ux * baseRadius;
            const sy = src.y + uy * baseRadius;
            const ex = tgt.x - ux * baseRadius;
            const ey = tgt.y - uy * baseRadius;

            ctx.moveTo(sx, sy);
            ctx.lineTo(ex, ey);
            ctx.stroke();

            // Arrowhead for directed edges
            if (e.directed) {
                const arrowLen = 10;
                const arrowAngle = Math.PI / 7;
                const angle = Math.atan2(ey - sy, ex - sx);

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
        });
    }
}
