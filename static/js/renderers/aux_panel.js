class AuxPanelRenderer {
    constructor(container) {
        this.container = container;
    }

    render(auxPanels) {
        this.container.innerHTML = '';
        if (!auxPanels || auxPanels.length === 0) {
            this.container.style.display = 'none';
            return;
        }
        this.container.style.display = 'flex';

        auxPanels.forEach(panel => {
            const panelEl = document.createElement('div');
            panelEl.className = 'aux-panel';

            const titleEl = document.createElement('div');
            titleEl.className = 'aux-panel-title';
            titleEl.textContent = panel.title;
            panelEl.appendChild(titleEl);

            const itemsEl = document.createElement('div');
            itemsEl.className = 'aux-panel-items';

            panel.items.forEach(item => {
                const itemEl = document.createElement('div');
                itemEl.className = 'aux-panel-item';
                if (item.selected) itemEl.classList.add('aux-selected');
                if (item.patched) itemEl.classList.add('aux-patched');
                if (item.error) itemEl.classList.add('aux-error');
                itemEl.textContent = item.label || String(item.value);
                itemsEl.appendChild(itemEl);
            });

            panelEl.appendChild(itemsEl);
            this.container.appendChild(panelEl);
        });
    }
}
