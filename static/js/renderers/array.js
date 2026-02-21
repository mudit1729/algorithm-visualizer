class ArrayRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
    }

    render(step) {
        if (!step.array) return;

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

        const arr = step.array;
        const n = arr.length;
        if (n === 0) return;

        const maxVal = Math.max(...arr.map(c => Math.abs(c.value)), 1);
        const padding = 60;
        const barWidth = Math.min((W - padding * 2) / n, 60);
        const maxBarHeight = H - padding * 2 - 30;
        const totalW = barWidth * n;
        const offsetX = (W - totalW) / 2;
        const baseY = H - padding;

        const colors = {
            normal: '#89b4fa',
            selected: '#f9e2af',
            patched: '#a6e3a1',
            error: '#f38ba8',
            text: '#cdd6f4',
            label: '#6c7086',
        };

        for (let i = 0; i < n; i++) {
            const cell = arr[i];
            const x = offsetX + i * barWidth;
            const barH = (Math.abs(cell.value) / maxVal) * maxBarHeight;
            const y = baseY - barH;

            let fill = colors.normal;
            if (cell.error) fill = colors.error;
            else if (cell.patched) fill = colors.patched;
            else if (cell.selected) fill = colors.selected;

            const gap = 2;
            ctx.fillStyle = fill;
            ctx.beginPath();
            ctx.roundRect(x + gap, y, barWidth - gap * 2, barH, [4, 4, 0, 0]);
            ctx.fill();

            // Value label on top
            ctx.fillStyle = colors.text;
            ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            ctx.fillText(String(cell.value), x + barWidth / 2, y - 4);

            // Index label below
            ctx.fillStyle = colors.label;
            ctx.textBaseline = 'top';
            ctx.fillText(String(i), x + barWidth / 2, baseY + 6);
        }
    }
}
