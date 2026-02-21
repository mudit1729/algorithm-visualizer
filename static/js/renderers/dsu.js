class DSURenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
    }

    render(step) {
        if (!step.dsu_nodes) return;

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

        const nodes = step.dsu_nodes;

        const colors = {
            nodeFill: '#313244',
            nodeStroke: '#585b70',
            nodeText: '#cdd6f4',
            selected: '#f9e2af',
            patched: '#a6e3a1',
            error: '#f38ba8',
            edgeColor: '#585b70',
            rankText: '#6c7086',
        };

        // Build forest: identify roots and children
        const children = {};
        const nodeMap = {};
        const roots = [];
        nodes.forEach(n => {
            nodeMap[n.id] = n;
            children[n.id] = [];
        });
        nodes.forEach(n => {
            if (n.parent_id == null) {
                roots.push(n.id);
            } else {
                if (children[n.parent_id]) {
                    children[n.parent_id].push(n.id);
                }
            }
        });

        const nodeRadius = Math.min(38, Math.max(20, 260 / Math.sqrt(nodes.length)));
        const levelHeight = nodeRadius * 3.5;
        const padding = 40;

        // Count leaves per subtree
        function countLeaves(id) {
            const ch = children[id] || [];
            if (ch.length === 0) return 1;
            return ch.reduce((sum, c) => sum + countLeaves(c), 0);
        }

        const treeSizes = roots.map(r => countLeaves(r));
        const totalLeaves = treeSizes.reduce((a, b) => a + b, 1);
        const availW = W - padding * 2;

        const positions = {};
        let xCursor = padding;

        roots.forEach((rootId, ti) => {
            const treeW = Math.max((treeSizes[ti] / totalLeaves) * availW, nodeRadius * 3);
            layoutTree(rootId, xCursor, xCursor + treeW, padding + nodeRadius);
            xCursor += treeW;
        });

        function layoutTree(id, xMin, xMax, y) {
            const ch = children[id] || [];
            if (ch.length === 0) {
                positions[id] = { x: (xMin + xMax) / 2, y };
                return;
            }
            const childLeaves = ch.map(c => countLeaves(c));
            const totalCh = childLeaves.reduce((a, b) => a + b, 1);
            let cx = xMin;
            ch.forEach((cid, i) => {
                const cw = (childLeaves[i] / totalCh) * (xMax - xMin);
                layoutTree(cid, cx, cx + cw, y + levelHeight);
                cx += cw;
            });
            const firstChild = positions[ch[0]];
            const lastChild = positions[ch[ch.length - 1]];
            positions[id] = { x: (firstChild.x + lastChild.x) / 2, y };
        }

        // Draw edges (parent → child lines)
        nodes.forEach(n => {
            if (n.parent_id != null && positions[n.id] && positions[n.parent_id]) {
                const parent = positions[n.parent_id];
                const child = positions[n.id];
                ctx.beginPath();
                ctx.strokeStyle = colors.edgeColor;
                ctx.lineWidth = 1.5;
                ctx.moveTo(parent.x, parent.y + nodeRadius);
                ctx.lineTo(child.x, child.y - nodeRadius);
                ctx.stroke();
            }
        });

        // Compute uniform font size based on longest label
        const maxLabelLen = nodes.reduce((mx, n) => Math.max(mx, (n.label || '').length), 1);
        const uniformFontSize = maxLabelLen > 4
            ? Math.floor(nodeRadius * Math.min(0.75, 2.8 / maxLabelLen))
            : Math.floor(nodeRadius * 0.75);

        // Draw nodes
        nodes.forEach(n => {
            const pos = positions[n.id];
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
            ctx.arc(x, y, nodeRadius, 0, Math.PI * 2);
            ctx.fillStyle = fillColor;
            ctx.fill();
            ctx.shadowColor = 'transparent';

            ctx.lineWidth = strokeWidth;
            ctx.strokeStyle = strokeColor;
            ctx.stroke();

            // Label (uniform size across all nodes)
            ctx.fillStyle = textColor;
            ctx.font = `bold ${uniformFontSize}px -apple-system, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(n.label, x, y);

        });
    }
}
