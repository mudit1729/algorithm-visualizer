class Player {
    constructor(onStepChanged) {
        this.steps = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.intervalId = null;
        this.speedMs = 400;
        this.onStepChanged = onStepChanged;
        this.onExternalNotify = null;   // set by voice.js for bidirectional sync
        this._suppressExternal = false; // true during voice-agent-driven actions
        this._rangeTarget = undefined;
    }

    load(steps) {
        this.pause();
        this.steps = steps;
        this.currentIndex = 0;
        this.notify();
    }

    play() {
        if (this.steps.length === 0) return;
        if (this.currentIndex >= this.steps.length - 1) {
            this.currentIndex = 0;
        }
        this.isPlaying = true;
        this.intervalId = setInterval(() => this.autoStep(), this.speedMs);
        this.notify();
    }

    pause() {
        this.isPlaying = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.notify();
    }

    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    stepForward() {
        if (this.currentIndex < this.steps.length - 1) {
            this.currentIndex++;
            this.notify();
        }
    }

    stepBack() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.notify();
        }
    }

    goToStart() {
        this.pause();
        this.currentIndex = 0;
        this.notify();
    }

    goToEnd() {
        this.pause();
        if (this.steps.length > 0) {
            this.currentIndex = this.steps.length - 1;
        }
        this.notify();
    }

    goToIndex(index) {
        if (index >= 0 && index < this.steps.length) {
            this.currentIndex = index;
            this.notify();
        }
    }

    setSpeed(sliderValue) {
        // Slider goes 1..20: 1 = slow (1200ms), 20 = fast (30ms)
        this.speedMs = Math.round(1200 / sliderValue);
        if (this.isPlaying) {
            clearInterval(this.intervalId);
            this.intervalId = setInterval(() => this.autoStep(), this.speedMs);
        }
    }

    autoStep() {
        if (this.currentIndex < this.steps.length - 1) {
            this.currentIndex++;
            this.notify();
        } else {
            this.pause();
        }
    }

    playRange(fromIndex, toIndex) {
        if (this.steps.length === 0) return Promise.resolve();
        fromIndex = Math.max(0, Math.min(fromIndex, this.steps.length - 1));
        toIndex = Math.max(0, Math.min(toIndex, this.steps.length - 1));

        this.pause();
        this.currentIndex = fromIndex;
        this._rangeTarget = toIndex;
        this.isPlaying = true;
        this.intervalId = setInterval(() => this._rangeStep(), this.speedMs);
        this.notify();
    }

    _rangeStep() {
        if (this._rangeTarget !== undefined && this.currentIndex >= this._rangeTarget) {
            this._rangeTarget = undefined;
            this.pause();
            return;
        }
        if (this.currentIndex < this.steps.length - 1) {
            this.currentIndex++;
            this.notify();
        } else {
            this._rangeTarget = undefined;
            this.pause();
        }
    }

    notify() {
        if (this.steps.length > 0) {
            this.onStepChanged(
                this.steps[this.currentIndex],
                this.currentIndex,
                this.steps.length,
                this.isPlaying
            );
            if (this.onExternalNotify && !this._suppressExternal) {
                this.onExternalNotify(this.currentIndex, this.steps.length, this.isPlaying);
            }
        }
    }

    get currentStep() {
        return this.steps.length > 0 ? this.steps[this.currentIndex] : null;
    }
}
