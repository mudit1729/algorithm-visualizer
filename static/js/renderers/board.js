class BoardRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
    }

    render(step) {
        if (!step.board) return;

        const canvas = this.canvas;
        const ctx = this.ctx;

        // Set canvas size to match CSS size (handle HiDPI)
        const rect = canvas.parentElement.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const W = rect.width;
        const H = rect.height;

        // Clear
        ctx.clearRect(0, 0, W, H);

        const rows = step.board.length;
        const cols = step.board[0].length;

        // Calculate cell size
        const maxCellSize = 72;
        const padding = 50;
        const cellSize = Math.min(
            (W - padding * 2) / cols,
            (H - padding * 2) / rows,
            maxCellSize
        );

        const boardW = cols * cellSize;
        const boardH = rows * cellSize;
        const offsetX = (W - boardW) / 2;
        const offsetY = (H - boardH) / 2;

        // Colors
        const colors = {
            cellLight: '#313244',
            cellDark: '#45475a',
            queen: '#a6e3a1',
            land: '#a6e3a1',
            water: '#1e3a5f',
            selected: 'rgba(249, 226, 175, 0.5)',
            patched: 'rgba(137, 180, 250, 0.6)',
            error: 'rgba(243, 139, 168, 0.6)',
            queenText: '#1e1e2e',
            label: '#6c7086',
            border: '#585b70',
        };

        // Detect mode: string values = grid problem, integer values = chess/queen
        const isGridProblem = step.board.some(row =>
            row.some(c => typeof c.value === 'string')
        );

        // Grid value-to-color mapping
        const gridColors = {
            '1': colors.land,       // land / fresh orange
            '0': colors.water,      // water / empty / blocked
            '2': '#fab387',         // rotten orange / special
            'X': '#585b70',         // wall / blocked
            'O': colors.land,       // open region
            'S': '#89dceb',         // safe / marked
            'W': '#585b70',         // wall
            '.': '#313244',         // empty room
        };

        // Draw board shadow
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = 20;
        ctx.shadowOffsetY = 4;
        ctx.fillStyle = colors.cellLight;
        ctx.fillRect(offsetX, offsetY, boardW, boardH);
        ctx.shadowColor = 'transparent';

        // Draw cells
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const cell = step.board[r][c];
                const x = offsetX + c * cellSize;
                const y = offsetY + r * cellSize;

                if (isGridProblem) {
                    // Grid mode: color by value
                    const baseColor = gridColors[cell.value] || colors.cellLight;
                    ctx.fillStyle = baseColor;
                    ctx.fillRect(x, y, cellSize, cellSize);

                    // State overlays
                    if (cell.error) {
                        ctx.fillStyle = colors.error;
                        ctx.fillRect(x, y, cellSize, cellSize);
                    } else if (cell.patched) {
                        ctx.fillStyle = colors.patched;
                        ctx.fillRect(x, y, cellSize, cellSize);
                    } else if (cell.selected) {
                        ctx.fillStyle = colors.selected;
                        ctx.fillRect(x, y, cellSize, cellSize);
                    }

                    // Label: show value for non-trivial cells
                    const val = String(cell.value);
                    if (val && val !== '0' && val !== '.') {
                        ctx.fillStyle = 'rgba(0,0,0,0.5)';
                        ctx.font = `bold ${Math.floor(cellSize * 0.32)}px -apple-system, sans-serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(val, x + cellSize / 2, y + cellSize / 2);
                    }
                } else {
                    // Chess/queen mode: checkerboard
                    const isLight = (r + c) % 2 === 0;
                    ctx.fillStyle = isLight ? colors.cellLight : colors.cellDark;
                    ctx.fillRect(x, y, cellSize, cellSize);

                    // State overlays
                    if (cell.error) {
                        ctx.fillStyle = colors.error;
                        ctx.fillRect(x, y, cellSize, cellSize);
                    } else if (cell.patched) {
                        ctx.fillStyle = colors.patched;
                        ctx.fillRect(x, y, cellSize, cellSize);
                    } else if (cell.selected) {
                        ctx.fillStyle = colors.selected;
                        ctx.fillRect(x, y, cellSize, cellSize);
                    }

                    // Queen symbol
                    if (cell.value === 1) {
                        if (!cell.error && !cell.patched && !cell.selected) {
                            ctx.fillStyle = colors.queen;
                            ctx.fillRect(x, y, cellSize, cellSize);
                        }

                        ctx.fillStyle = cell.error ? '#fff' : colors.queenText;
                        ctx.font = `${Math.floor(cellSize * 0.55)}px serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('\u265B', x + cellSize / 2, y + cellSize / 2 + 1);
                    }
                }

                // Cell border
                ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
                ctx.lineWidth = 0.5;
                ctx.strokeRect(x, y, cellSize, cellSize);
            }
        }

        // Outer border
        ctx.strokeStyle = colors.border;
        ctx.lineWidth = 2;
        ctx.strokeRect(offsetX, offsetY, boardW, boardH);

        // Row/col labels
        ctx.font = '11px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.fillStyle = colors.label;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        for (let r = 0; r < rows; r++) {
            ctx.fillText(
                String(r),
                offsetX - 18,
                offsetY + r * cellSize + cellSize / 2
            );
        }
        for (let c = 0; c < cols; c++) {
            ctx.fillText(
                String(c),
                offsetX + c * cellSize + cellSize / 2,
                offsetY - 18
            );
        }
    }
}
