class TrieRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
    }

    render(step) {
        if (!step.trie_nodes) return;

        const canvas = this.canvas;
        const ctx = this.ctx;

        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const W = rect.width;
        const H = rect.height;
        ctx.clearRect(0, 0, W, H);

        const nodes = step.trie_nodes;
        const edges = step.trie_edges || [];

        const padding = 40;
        const areaW = W - padding * 2;
        const areaH = H - padding * 2;

        const nodeMap = {};
        nodes.forEach(n => {
            nodeMap[n.id] = {
                x: padding + n.x * areaW,
                y: padding + n.y * areaH,
                node: n,
            };
        });

        const nodeR = Math.min(18, Math.max(10, 150 / Math.sqrt(nodes.length)));

        const colors = {
            nodeFill: '#313244',
            nodeStroke: '#585b70',
            nodeText: '#cdd6f4',
            selected: '#f9e2af',
            patched: '#a6e3a1',
            error: '#f38ba8',
            endRing: '#a6e3a1',
            edgeDefault: '#585b70',
            edgeSelected: '#f9e2af',
            edgePatched: '#89b4fa',
            edgeLabel: '#89b4fa',
        };

        // Draw edges
        edges.forEach(e => {
            const src = nodeMap[e.source];
            const tgt = nodeMap[e.target];
            if (!src || !tgt) return;

            let strokeColor = colors.edgeDefault;
            let lineWidth = 1.5;
            if (e.error) {
                strokeColor = colors.error;
                lineWidth = 2.5;
            } else if (e.selected) {
                strokeColor = colors.edgeSelected;
                lineWidth = 2.5;
            } else if (e.patched) {
                strokeColor = colors.edgePatched;
                lineWidth = 2;
            }

            const dx = tgt.x - src.x;
            const dy = tgt.y - src.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 0.1) return;

            const ux = dx / dist;
            const uy = dy / dist;
            const sx = src.x + ux * nodeR;
            const sy = src.y + uy * nodeR;
            const ex = tgt.x - ux * nodeR;
            const ey = tgt.y - uy * nodeR;

            ctx.beginPath();
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = lineWidth;
            ctx.moveTo(sx, sy);
            ctx.lineTo(ex, ey);
            ctx.stroke();

            // Edge label (character)
            if (e.label) {
                const mx = (sx + ex) / 2;
                const my = (sy + ey) / 2;
                const fontSize = Math.max(10, Math.floor(nodeR * 0.9));
                ctx.font = `bold ${fontSize}px -apple-system, sans-serif`;
                const tw = ctx.measureText(e.label).width + 8;
                // Background pill
                ctx.fillStyle = '#1e1e2e';
                ctx.beginPath();
                ctx.roundRect(mx - tw / 2, my - fontSize * 0.7, tw, fontSize * 1.4, 3);
                ctx.fill();
                // Text
                ctx.fillStyle = colors.edgeLabel;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(e.label, mx, my);
            }
        });

        // Draw nodes
        nodes.forEach(n => {
            const pos = nodeMap[n.id];
            if (!pos) return;
            const x = pos.x;
            const y = pos.y;

            let fillColor = colors.nodeFill;
            let strokeColor = colors.nodeStroke;
            let textColor = colors.nodeText;
            let strokeWidth = 2;

            if (n.error) {
                fillColor = colors.error;
                strokeColor = colors.error;
                textColor = '#fff';
                strokeWidth = 3;
            } else if (n.selected) {
                strokeColor = colors.selected;
                strokeWidth = 3;
                fillColor = 'rgba(249, 226, 175, 0.2)';
            } else if (n.patched) {
                fillColor = colors.patched;
                strokeColor = colors.patched;
                textColor = '#1e1e2e';
            }

            // Shadow
            ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
            ctx.shadowBlur = 6;
            ctx.shadowOffsetY = 2;

            ctx.beginPath();
            ctx.arc(x, y, nodeR, 0, Math.PI * 2);
            ctx.fillStyle = fillColor;
            ctx.fill();
            ctx.shadowColor = 'transparent';

            ctx.lineWidth = strokeWidth;
            ctx.strokeStyle = strokeColor;
            ctx.stroke();

            // Double ring for is_end nodes
            if (n.is_end) {
                ctx.beginPath();
                ctx.arc(x, y, nodeR + 4, 0, Math.PI * 2);
                ctx.strokeStyle = colors.endRing;
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // Label
            if (n.label) {
                ctx.fillStyle = textColor;
                ctx.font = `bold ${Math.floor(nodeR * 0.8)}px -apple-system, sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(n.label, x, y);
            }
        });
    }
}
