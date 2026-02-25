class CodePanel {
    constructor(containerEl) {
        this.container = containerEl;
        this.lines = [];
    }

    loadCode(source) {
        this.container.innerHTML = '';
        const rawLines = source.split('\n');
        this.lines = [];

        rawLines.forEach((text, i) => {
            const lineEl = document.createElement('span');
            lineEl.className = 'code-line';

            const numEl = document.createElement('span');
            numEl.className = 'line-number';
            numEl.textContent = String(i + 1);

            const codeEl = document.createElement('span');
            codeEl.className = 'code-text';
            codeEl.innerHTML = this.highlightSyntax(text);

            lineEl.appendChild(numEl);
            lineEl.appendChild(codeEl);
            this.container.appendChild(lineEl);
            this.lines.push(lineEl);
        });
    }

    highlightLine(lineNumber) {
        this.lines.forEach((el, i) => {
            if (i + 1 === lineNumber) {
                el.classList.add('active');
                el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            } else {
                el.classList.remove('active');
            }
        });
    }

    highlightSyntax(text) {
        // Tokenize-based approach: split into tokens first, then wrap each.
        // This avoids cascading regex issues where later patterns match inside
        // previously inserted <span> tags.

        const keywords = new Set(['def', 'return', 'if', 'else', 'elif', 'for', 'while',
            'in', 'range', 'and', 'or', 'not', 'break', 'continue', 'class',
            'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'yield',
            'lambda', 'pass', 'raise', 'global', 'nonlocal', 'assert', 'del']);
        const booleans = new Set(['True', 'False', 'None']);

        // Tokenization regex: matches comments, strings, words, numbers, operators, whitespace, other
        const tokenRe = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|([a-zA-Z_]\w*)|(\d+)|(==|!=|<=|>=|<|>|\+=|-=|\*=)|(\s+)|(.)/gm;

        let result = '';
        let match;
        while ((match = tokenRe.exec(text)) !== null) {
            const [full, comment, str, word, num, op, ws, other] = match;

            if (comment) {
                result += `<span class="syn-comment">${this.esc(comment)}</span>`;
            } else if (str) {
                result += `<span class="syn-string">${this.esc(str)}</span>`;
            } else if (word) {
                if (keywords.has(word)) {
                    result += `<span class="syn-keyword">${word}</span>`;
                } else if (booleans.has(word)) {
                    result += `<span class="syn-bool">${word}</span>`;
                } else {
                    // Check if followed by '(' — function call
                    const rest = text.slice(tokenRe.lastIndex);
                    if (/^\s*\(/.test(rest)) {
                        result += `<span class="syn-function">${word}</span>`;
                    } else {
                        result += word;
                    }
                }
            } else if (num) {
                result += `<span class="syn-number">${num}</span>`;
            } else if (op) {
                result += `<span class="syn-operator">${this.esc(op)}</span>`;
            } else if (ws) {
                result += ws;
            } else if (other) {
                result += this.esc(other);
            }
        }

        return result;
    }

    highlightLines(startLine, endLine) {
        this.lines.forEach(el => el.classList.remove('voice-highlight'));
        for (let i = startLine - 1; i < endLine && i < this.lines.length; i++) {
            if (i >= 0) {
                this.lines[i].classList.add('voice-highlight');
                if (i === startLine - 1) {
                    this.lines[i].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                }
            }
        }
    }

    clearVoiceHighlight() {
        this.lines.forEach(el => el.classList.remove('voice-highlight'));
    }

    esc(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
}
