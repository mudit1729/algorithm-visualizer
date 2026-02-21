document.addEventListener('DOMContentLoaded', () => {
    // --- Screens ---
    const landingScreen = document.getElementById('landing-screen');
    const vizScreen = document.getElementById('viz-screen');

    // --- Landing elements ---
    const problemPicker = document.getElementById('problem-picker');
    const showcaseGallery = document.getElementById('showcase-gallery');
    const detailPanel = document.getElementById('detail-panel');
    const detailOverlay = document.getElementById('detail-overlay');
    const detailClose = document.getElementById('detail-close');
    const detailTopic = document.getElementById('detail-topic');
    const detailName = document.getElementById('detail-name');
    const detailDesc = document.getElementById('detail-desc');
    const visualizeBtn = document.getElementById('visualize-btn');

    // --- Viz elements ---
    const backBtn = document.getElementById('back-btn');
    const currentProblemName = document.getElementById('current-problem-name');
    const stepDescription = document.getElementById('step-description');
    const stepCounter = document.getElementById('step-counter');
    const progressFill = document.getElementById('progress-bar-fill');
    const progressContainer = document.getElementById('progress-bar-container');
    const btnStart = document.getElementById('btn-start');
    const btnBack = document.getElementById('btn-back');
    const btnPlay = document.getElementById('btn-play');
    const btnFwd = document.getElementById('btn-fwd');
    const btnEnd = document.getElementById('btn-end');
    const speedSlider = document.getElementById('speed-slider');
    const canvas = document.getElementById('viz-canvas');
    const codeDisplay = document.getElementById('code-display');
    const logContent = document.getElementById('log-content');
    const logDrawer = document.getElementById('log-drawer');
    const logToggle = document.getElementById('log-toggle');

    // --- State ---
    let problems = [];
    let selectedProblem = null;
    let currentRenderer = null;
    let onVizScreen = false;
    const codePanel = new CodePanel(codeDisplay);
    const auxContainer = document.getElementById('aux-panel-container');
    const auxRenderer = new AuxPanelRenderer(auxContainer);

    // --- Player ---
    const player = new Player((step, index, total, isPlaying) => {
        if (currentRenderer) {
            currentRenderer.render(step);
        }
        auxRenderer.render(step.aux_panels || []);
        codePanel.highlightLine(step.line_number);
        stepDescription.textContent = step.description || '';
        stepCounter.textContent = `Step ${index + 1} / ${total}`;
        const pct = total > 1 ? (index / (total - 1)) * 100 : 0;
        progressFill.style.width = pct + '%';
        btnPlay.textContent = isPlaying ? '\u23F8' : '\u25B6';
        btnPlay.classList.toggle('playing', isPlaying);
        updateLog(step.log_messages || []);
    });

    function updateLog(messages) {
        logContent.innerHTML = '';
        const toShow = messages.slice(-50);
        toShow.forEach(msg => {
            const el = document.createElement('div');
            el.className = 'log-entry';
            el.textContent = msg;
            logContent.appendChild(el);
        });
        logContent.scrollTop = logContent.scrollHeight;
    }

    // --- Screen transitions ---
    function showLanding() {
        player.pause();
        onVizScreen = false;
        vizScreen.classList.add('hidden');
        landingScreen.classList.remove('hidden');
    }

    function showViz() {
        onVizScreen = true;
        closeDetailPanel();
        landingScreen.classList.add('hidden');
        vizScreen.classList.remove('hidden');
    }

    // --- Detail panel open/close ---
    function formatDescription(text) {
        if (!text) return '';
        // Split into paragraphs on double newline
        const paragraphs = text.split(/\n\n+/);
        let html = '';
        for (const para of paragraphs) {
            const trimmed = para.trim();
            if (!trimmed) continue;

            // Detect "Constraints:" header
            if (/^Constraints:?\s*$/i.test(trimmed)) {
                html += `<div class="example-label">Constraints</div>`;
                continue;
            }

            // Detect constraint lists (lines starting with - or bullet)
            if (/^\s*[-•]/.test(trimmed)) {
                const items = trimmed.split(/\n/).map(l => l.replace(/^\s*[-•]\s*/, '').trim()).filter(Boolean);
                html += '<ul class="constraint-list">' + items.map(i => `<li>${inlineFmt(i)}</li>`).join('') + '</ul>';
                continue;
            }

            // Detect example blocks: starts with "Example N:" followed by Input:/Output: lines
            const exMatch = trimmed.match(/^(Example\s*\d*):?\s*\n/i);
            if (exMatch) {
                html += `<div class="example-label">${exMatch[1]}</div>`;
                const body = trimmed.slice(exMatch[0].length).trim();
                // Split lines and format each
                const lines = body.split(/\n/).map(l => inlineFmt(l.trim()));
                html += `<div class="example-block">${lines.join('<br>')}</div>`;
                continue;
            }

            // Check if paragraph has Input:/Output: without Example label
            if (/^\s*(Input|Output|Explanation):/m.test(trimmed)) {
                const lines = trimmed.split(/\n/).map(l => inlineFmt(l.trim()));
                html += `<div class="example-block">${lines.join('<br>')}</div>`;
                continue;
            }

            // Regular paragraph - apply inline formatting
            html += `<p>${inlineFmt(trimmed)}</p>`;
        }
        return html;
    }

    function inlineFmt(text) {
        let s = escapeHtml(text);
        // Inline code: `text`
        s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Bold: **text**
        s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        return s;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function openDetailPanel(problem) {
        selectedProblem = problem;

        detailTopic.textContent = `${problem.topic} / ${problem.subtopic}`;
        detailName.textContent = problem.name;
        detailDesc.innerHTML = formatDescription(problem.long_description || problem.description);

        detailPanel.classList.add('open');
        detailOverlay.classList.remove('hidden');
        // Trigger reflow before adding visible class for transition
        void detailOverlay.offsetWidth;
        detailOverlay.classList.add('visible');
    }

    function closeDetailPanel() {
        detailPanel.classList.remove('open');
        detailOverlay.classList.remove('visible');
        setTimeout(() => {
            detailOverlay.classList.add('hidden');
        }, 300);
    }

    // --- Explicit topic display order ---
    const TOPIC_ORDER = [
        "Graph / DFS", "Graph / BFS", "Topological Sort", "Backtracking",
        "Dynamic Programming", "Shortest Path", "Minimum Spanning Tree",
        "Greedy", "Tree / BFS", "Trie", "Union Find",
    ];

    // --- Build problem picker (grouped by topic > subtopic) ---
    function buildPicker(problems) {
        problemPicker.innerHTML = '';

        // Group: topic -> subtopic -> [problems]
        const groups = new Map();
        problems.forEach(p => {
            if (!groups.has(p.topic)) groups.set(p.topic, new Map());
            const topicMap = groups.get(p.topic);
            if (!topicMap.has(p.subtopic)) topicMap.set(p.subtopic, []);
            topicMap.get(p.subtopic).push(p);
        });

        // Sort by explicit order; unknown topics go at the end
        const sorted = new Map();
        TOPIC_ORDER.forEach(t => { if (groups.has(t)) sorted.set(t, groups.get(t)); });
        groups.forEach((v, t) => { if (!sorted.has(t)) sorted.set(t, v); });

        sorted.forEach((subtopics, topic) => {
            const topicDiv = document.createElement('div');
            topicDiv.className = 'topic-group';

            const topicLabel = document.createElement('div');
            topicLabel.className = 'topic-label';
            topicLabel.textContent = topic;
            topicDiv.appendChild(topicLabel);

            subtopics.forEach((probs, subtopic) => {
                const subDiv = document.createElement('div');
                subDiv.className = 'subtopic-group';

                const subLabel = document.createElement('div');
                subLabel.className = 'subtopic-label';
                subLabel.textContent = subtopic;
                subDiv.appendChild(subLabel);

                probs.forEach(p => {
                    const card = document.createElement('div');
                    card.className = 'problem-card';
                    card.dataset.name = p.name;
                    card.innerHTML = `
                        <span class="problem-card-name">${p.name}</span>
                        <span class="problem-card-desc">${p.description}</span>
                        <span class="problem-card-arrow">&rarr;</span>
                    `;
                    card.addEventListener('click', () => {
                        document.querySelectorAll('.problem-card').forEach(c => c.classList.remove('selected'));
                        card.classList.add('selected');
                        openDetailPanel(p);
                    });
                    subDiv.appendChild(card);
                });

                topicDiv.appendChild(subDiv);
            });

            problemPicker.appendChild(topicDiv);
        });
    }

    // --- Showcase gallery data ---
    const SHOWCASE_ITEMS = [
        { problem: "Dijkstra's Shortest Path", img: "/screenshots/dijkstra.png", caption: "Dijkstra's Shortest Path" },
        { problem: "N-Queens", img: "/screenshots/n_queens.png", caption: "N-Queens" },
        { problem: "Implement Trie", img: "/screenshots/implement_trie.png", caption: "Implement Trie" },
    ];

    function buildShowcase(problems) {
        showcaseGallery.innerHTML = '';
        SHOWCASE_ITEMS.forEach(item => {
            const card = document.createElement('div');
            card.className = 'showcase-card';

            const img = document.createElement('img');
            img.src = item.img;
            img.alt = item.caption;
            img.loading = 'lazy';
            card.appendChild(img);

            const caption = document.createElement('div');
            caption.className = 'showcase-card-caption';
            caption.textContent = item.caption;
            card.appendChild(caption);

            // Clicking a showcase card opens the problem detail panel
            card.addEventListener('click', () => {
                const p = problems.find(prob => prob.name === item.problem);
                if (p) {
                    document.querySelectorAll('.problem-card').forEach(c => c.classList.remove('selected'));
                    const matchCard = document.querySelector(`.problem-card[data-name="${p.name}"]`);
                    if (matchCard) {
                        matchCard.classList.add('selected');
                        matchCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    openDetailPanel(p);
                }
            });

            showcaseGallery.appendChild(card);
        });
    }

    // --- Run problem ---
    async function runProblem() {
        if (!selectedProblem) return;

        const name = selectedProblem.name;
        const params = selectedProblem.default_params || {};

        visualizeBtn.textContent = '...';
        visualizeBtn.disabled = true;

        try {
            const res = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ problem: name, params, compact: true }),
            });
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            // Switch to viz screen
            currentProblemName.textContent = name;
            showViz();

            // Set up renderer
            if (data.renderer_type === 'board') {
                currentRenderer = new BoardRenderer(canvas);
            } else if (data.renderer_type === 'array') {
                currentRenderer = new ArrayRenderer(canvas);
            } else if (data.renderer_type === 'graph') {
                currentRenderer = new GraphRenderer(canvas);
            } else if (data.renderer_type === 'dsu') {
                currentRenderer = new DSURenderer(canvas);
            } else if (data.renderer_type === 'trie') {
                currentRenderer = new TrieRenderer(canvas);
            }

            // Load code
            codePanel.loadCode(data.source_code);

            // Wait a frame so the canvas has layout dimensions
            requestAnimationFrame(() => {
                player.load(data.steps);
            });
        } catch (err) {
            console.error('Run error:', err);
            alert('Error running problem: ' + err.message);
        } finally {
            visualizeBtn.textContent = 'Visualize';
            visualizeBtn.disabled = false;
        }
    }

    // --- Log drawer toggle ---
    logToggle.addEventListener('click', () => {
        const isCollapsed = logDrawer.classList.contains('log-collapsed');
        logDrawer.classList.toggle('log-collapsed', !isCollapsed);
        logDrawer.classList.toggle('log-expanded', isCollapsed);
        logToggle.innerHTML = isCollapsed ? '&laquo;' : '&raquo;';
        // Re-render canvas after layout shift
        setTimeout(() => {
            if (player.currentStep && currentRenderer) {
                currentRenderer.render(player.currentStep);
            }
        }, 220);
    });

    // --- Event listeners ---
    visualizeBtn.addEventListener('click', runProblem);
    detailClose.addEventListener('click', closeDetailPanel);
    detailOverlay.addEventListener('click', closeDetailPanel);
    backBtn.addEventListener('click', showLanding);

    btnStart.addEventListener('click', () => player.goToStart());
    btnBack.addEventListener('click', () => player.stepBack());
    btnPlay.addEventListener('click', () => player.togglePlay());
    btnFwd.addEventListener('click', () => player.stepForward());
    btnEnd.addEventListener('click', () => player.goToEnd());

    speedSlider.addEventListener('input', (e) => {
        player.setSpeed(parseInt(e.target.value));
    });

    // Progress bar click to seek
    progressContainer.addEventListener('click', (e) => {
        const rect = progressContainer.getBoundingClientRect();
        const ratio = (e.clientX - rect.left) / rect.width;
        const index = Math.round(ratio * (player.steps.length - 1));
        player.goToIndex(index);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.code === 'Escape') {
            if (onVizScreen) {
                showLanding();
            } else if (detailPanel.classList.contains('open')) {
                closeDetailPanel();
            }
            return;
        }

        if (!onVizScreen) return;

        switch (e.code) {
            case 'Space':
                e.preventDefault();
                player.togglePlay();
                break;
            case 'ArrowRight':
                e.preventDefault();
                player.stepForward();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                player.stepBack();
                break;
            case 'Home':
                e.preventDefault();
                player.goToStart();
                break;
            case 'End':
                e.preventDefault();
                player.goToEnd();
                break;
        }
    });

    // Handle window resize for canvas
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (player.currentStep && currentRenderer) {
                currentRenderer.render(player.currentStep);
            }
        }, 100);
    });

    // --- Divider drag to resize ---
    const divider = document.getElementById('divider');
    const codePanelEl = document.getElementById('code-panel');
    let isDragging = false;

    divider.addEventListener('mousedown', (e) => {
        isDragging = true;
        divider.classList.add('active');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const mainContent = document.getElementById('main-content');
        const mainRect = mainContent.getBoundingClientRect();
        const newWidth = mainRect.right - e.clientX;
        const clampedWidth = Math.max(320, Math.min(700, newWidth));
        codePanelEl.style.width = clampedWidth + 'px';

        if (player.currentStep && currentRenderer) {
            currentRenderer.render(player.currentStep);
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            divider.classList.remove('active');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });

    // --- Init: load problem list and build showcase ---
    async function init() {
        const res = await fetch('/api/problems');
        problems = await res.json();
        buildPicker(problems);
        buildShowcase(problems);
    }

    init();
});
