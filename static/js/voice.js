/* ============================================================
   voice.js — OpenAI Realtime API voice tutor integration
   Manages WebRTC connection + voice panel UI + tool dispatch
   ============================================================ */

const REALTIME_MODEL = 'gpt-4o-realtime-preview-2024-12-17';

// Cost rates
const COST_TEXT_INPUT  = 5.00  / 1_000_000;  // $/token
const COST_TEXT_OUTPUT = 20.00 / 1_000_000;
const COST_AUDIO_IN   = 0.06  / 60;          // $/second
const COST_AUDIO_OUT  = 0.24  / 60;

/* ----------------------------------------------------------
   RealtimeClient — WebRTC lifecycle + data channel events
   ---------------------------------------------------------- */
class RealtimeClient extends EventTarget {
    constructor() {
        super();
        this.pc = null;
        this.dc = null;
        this.audioEl = null;
        this.mediaStream = null;
        this.connected = false;
        this.sessionStartTime = null;
        this.usage = {
            inputTokens: 0,
            outputTokens: 0,
        };
    }

    async connect(token) {
        // 1. Peer connection
        this.pc = new RTCPeerConnection();

        // 2. Audio playback element for agent voice
        this.audioEl = document.createElement('audio');
        this.audioEl.autoplay = true;
        this.pc.ontrack = (e) => {
            this.audioEl.srcObject = e.streams[0];
        };

        // 3. Microphone
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
            });
        } catch (err) {
            const msg = err.name === 'NotAllowedError'
                ? 'Microphone permission denied. Please allow mic access and try again.'
                : err.name === 'NotFoundError'
                    ? 'No microphone found. Please connect a microphone.'
                    : `Microphone error: ${err.message}`;
            this._emit('error', { message: msg });
            this._cleanup();
            throw err;
        }
        this.mediaStream.getTracks().forEach(track => this.pc.addTrack(track, this.mediaStream));

        // 4. Data channel for events
        this.dc = this.pc.createDataChannel('oai-events');
        this.dc.onmessage = (e) => this._handleMessage(e);
        this.dc.onopen = () => {
            this.connected = true;
            this.sessionStartTime = Date.now();
            this._emit('connected', {});
        };
        this.dc.onclose = () => {
            this.connected = false;
            this._emit('disconnected', {});
        };

        // 5. SDP offer → OpenAI → answer
        const offer = await this.pc.createOffer();
        await this.pc.setLocalDescription(offer);

        const sdpResp = await fetch(
            `https://api.openai.com/v1/realtime?model=${REALTIME_MODEL}`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/sdp',
                },
                body: offer.sdp,
            }
        );

        if (!sdpResp.ok) {
            const text = await sdpResp.text();
            this._emit('error', { message: `SDP exchange failed: ${sdpResp.status} ${text}` });
            this._cleanup();
            throw new Error(`SDP exchange failed: ${sdpResp.status}`);
        }

        const answerSdp = await sdpResp.text();
        await this.pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });
    }

    disconnect() {
        this._cleanup();
        this._emit('disconnected', {});
    }

    sendFunctionResult(callId, result) {
        if (!this.dc || this.dc.readyState !== 'open') return;
        this.dc.send(JSON.stringify({
            type: 'conversation.item.create',
            item: {
                type: 'function_call_output',
                call_id: callId,
                output: JSON.stringify(result),
            },
        }));
        this.dc.send(JSON.stringify({
            type: 'response.create',
        }));
    }

    sendTextMessage(text) {
        if (!this.dc || this.dc.readyState !== 'open') return;
        this.dc.send(JSON.stringify({
            type: 'conversation.item.create',
            item: {
                type: 'message',
                role: 'user',
                content: [{ type: 'input_text', text }],
            },
        }));
        this.dc.send(JSON.stringify({
            type: 'response.create',
        }));
    }

    /* --- Private --- */

    _handleMessage(event) {
        let msg;
        try {
            msg = JSON.parse(event.data);
        } catch {
            return;
        }

        switch (msg.type) {
            case 'response.function_call_arguments.done':
                this._emit('function_call', {
                    name: msg.name,
                    args: JSON.parse(msg.arguments || '{}'),
                    callId: msg.call_id,
                });
                break;

            case 'response.done':
                if (msg.response && msg.response.usage) {
                    const u = msg.response.usage;
                    this.usage.inputTokens += (u.input_tokens || 0);
                    this.usage.outputTokens += (u.output_tokens || 0);
                    this._emit('usage_update', { usage: this.usage });
                }
                break;

            case 'response.audio_transcript.done':
                this._emit('transcript_done', {
                    role: 'agent',
                    text: msg.transcript || '',
                });
                break;

            case 'conversation.item.input_audio_transcription.completed':
                this._emit('user_transcript', {
                    role: 'user',
                    text: msg.transcript || '',
                });
                break;

            case 'error':
                this._emit('error', {
                    message: msg.error?.message || 'Unknown realtime error',
                    code: msg.error?.code,
                });
                break;
        }
    }

    _emit(name, detail) {
        this.dispatchEvent(new CustomEvent(name, { detail }));
    }

    _cleanup() {
        this.connected = false;
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(t => t.stop());
            this.mediaStream = null;
        }
        if (this.dc) {
            try { this.dc.close(); } catch {}
            this.dc = null;
        }
        if (this.pc) {
            try { this.pc.close(); } catch {}
            this.pc = null;
        }
        if (this.audioEl) {
            this.audioEl.srcObject = null;
            this.audioEl = null;
        }
    }
}


/* ----------------------------------------------------------
   VoiceUI — Panel DOM, session management, tool dispatch
   ---------------------------------------------------------- */
class VoiceUI {
    constructor() {
        this.client = null;
        this.isOpen = false;
        this.isConnected = false;
        this._audioTimer = null;
        this._audioSeconds = 0;
        this._buildUI();
    }

    /* --- DOM Construction --- */
    _buildUI() {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;

        // Drawer container
        this.drawer = document.createElement('div');
        this.drawer.id = 'voice-drawer';
        this.drawer.className = 'voice-collapsed';

        // Toggle button (>> / <<)
        this.toggleBtn = document.createElement('button');
        this.toggleBtn.id = 'voice-toggle';
        this.toggleBtn.title = 'Toggle voice tutor';
        this.toggleBtn.innerHTML = '&raquo;';
        this.toggleBtn.addEventListener('click', () => this.toggle());

        // Content panel
        const content = document.createElement('div');
        content.id = 'voice-drawer-content';

        // Header
        const header = document.createElement('div');
        header.className = 'voice-header';
        header.innerHTML = '<span>Voice Tutor</span>';
        this.costEl = document.createElement('span');
        this.costEl.id = 'voice-cost';
        this.costEl.textContent = '$0.000';
        header.appendChild(this.costEl);

        // Transcript area
        this.transcriptEl = document.createElement('div');
        this.transcriptEl.id = 'voice-transcript';

        // Status
        this.statusEl = document.createElement('div');
        this.statusEl.id = 'voice-status';
        this.statusEl.textContent = 'Click mic to start';

        // Mic button
        const controls = document.createElement('div');
        controls.className = 'voice-controls';
        this.micBtn = document.createElement('button');
        this.micBtn.id = 'voice-mic-btn';
        this.micBtn.title = 'Start voice session';
        this.micBtn.innerHTML = '&#x1F3A4;';
        this.micBtn.addEventListener('click', () => this._onMicClick());
        controls.appendChild(this.micBtn);

        // Assemble
        content.appendChild(header);
        content.appendChild(this.transcriptEl);
        content.appendChild(this.statusEl);
        content.appendChild(controls);

        this.drawer.appendChild(this.toggleBtn);
        this.drawer.appendChild(content);

        // Insert as first child of main-content (left edge)
        mainContent.insertBefore(this.drawer, mainContent.firstChild);
    }

    /* --- Toggle drawer open/close --- */
    toggle() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.drawer.classList.remove('voice-collapsed');
            this.drawer.classList.add('voice-expanded');
            this.toggleBtn.innerHTML = '&laquo;';
        } else {
            this.drawer.classList.remove('voice-expanded');
            this.drawer.classList.add('voice-collapsed');
            this.toggleBtn.innerHTML = '&raquo;';
        }
        // Re-render canvas after layout shift
        setTimeout(() => {
            const player = window.algoPlayer;
            if (player && player.currentStep) {
                // Trigger the renderer by notifying
                player.notify();
            }
        }, 220);
    }

    /* --- Mic button click: toggle session --- */
    async _onMicClick() {
        if (this.isConnected) {
            this.endSession();
        } else {
            await this.startSession();
        }
    }

    /* --- Start voice session --- */
    async startSession() {
        const problem = window.getSelectedProblem ? window.getSelectedProblem() : null;
        if (!problem) {
            this.statusEl.textContent = 'Load a problem first';
            return;
        }

        this.statusEl.textContent = 'Requesting session...';
        this.micBtn.disabled = true;

        try {
            // 1. Get ephemeral token
            const res = await fetch('/api/voice-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ problem_id: problem.name }),
            });
            const data = await res.json();

            if (data.error) {
                this.statusEl.textContent = `Error: ${data.error}`;
                this.micBtn.disabled = false;
                return;
            }

            // 2. Connect WebRTC
            this.statusEl.textContent = 'Connecting...';
            this.client = new RealtimeClient();

            this.client.addEventListener('connected', () => {
                this.isConnected = true;
                this.micBtn.classList.add('active');
                this.micBtn.disabled = false;
                this.statusEl.textContent = 'Connected — listening...';
                this._startAudioTimer();

                // Wire up bidirectional sync: player → agent
                const player = window.algoPlayer;
                if (player) {
                    player.onExternalNotify = (index, total, isPlaying) => {
                        if (!this.client || !this.client.connected) return;
                        const step = player.currentStep;
                        this.client.sendTextMessage(
                            `[User navigated to step ${index} of ${total - 1}. ` +
                            `Description: "${step?.description || ''}". ` +
                            `Playing: ${isPlaying}]`
                        );
                    };
                }

                // 3. Kick off the walkthrough
                this.client.sendTextMessage(
                    'Please begin walking through this algorithm visualization.'
                );
            });

            this.client.addEventListener('disconnected', () => {
                this._onDisconnected();
            });

            this.client.addEventListener('function_call', (e) => {
                this._handleFunctionCall(e.detail.name, e.detail.args, e.detail.callId);
            });

            this.client.addEventListener('transcript_done', (e) => {
                this._appendTranscript('agent', e.detail.text);
            });

            this.client.addEventListener('user_transcript', (e) => {
                this._appendTranscript('user', e.detail.text);
            });

            this.client.addEventListener('usage_update', () => {
                this._updateCost();
            });

            this.client.addEventListener('error', (e) => {
                console.error('Voice error:', e.detail);
                this.statusEl.textContent = `Error: ${e.detail.message}`;
            });

            await this.client.connect(data.token);
        } catch (err) {
            console.error('Voice session start error:', err);
            this.statusEl.textContent = 'Failed to connect';
            this.micBtn.disabled = false;
        }
    }

    /* --- End voice session --- */
    endSession() {
        if (this.client) {
            this.client.disconnect();
        }
        this._onDisconnected();
    }

    /* --- Handle disconnection cleanup --- */
    _onDisconnected() {
        this.isConnected = false;
        this.micBtn.classList.remove('active');
        this.micBtn.disabled = false;
        this.statusEl.textContent = 'Disconnected';
        this._stopAudioTimer();

        // Clear bidirectional sync
        const player = window.algoPlayer;
        if (player) {
            player.onExternalNotify = null;
        }

        // Clear voice highlights
        const cp = window.codePanel;
        if (cp) {
            cp.clearVoiceHighlight();
        }

        // Log session
        this._logSession();
    }

    /* --- Function call dispatch --- */
    _handleFunctionCall(name, args, callId) {
        const player = window.algoPlayer;
        const cp = window.codePanel;
        let result = {};

        // Suppress external notifications to avoid echo
        if (player) player._suppressExternal = true;

        switch (name) {
            case 'seek_to_step': {
                const idx = args.step_index;
                if (player) {
                    player.pause();
                    player.goToIndex(idx);
                    const step = player.currentStep;
                    result = {
                        success: true,
                        current_index: idx,
                        description: step?.description || '',
                    };
                } else {
                    result = { error: 'Player not available' };
                }
                break;
            }

            case 'highlight_code_lines': {
                if (cp) {
                    cp.highlightLines(args.start_line, args.end_line);
                    result = { success: true };
                } else {
                    result = { error: 'Code panel not available' };
                }
                break;
            }

            case 'play_steps': {
                if (player) {
                    player.playRange(args.from_step, args.to_step);
                    result = {
                        success: true,
                        playing_from: args.from_step,
                        playing_to: args.to_step,
                    };
                } else {
                    result = { error: 'Player not available' };
                }
                break;
            }

            case 'pause_player': {
                if (player) {
                    player.pause();
                    result = { success: true };
                } else {
                    result = { error: 'Player not available' };
                }
                break;
            }

            case 'get_current_state': {
                if (player) {
                    const step = player.currentStep;
                    result = {
                        current_index: player.currentIndex,
                        total_steps: player.steps.length,
                        is_playing: player.isPlaying,
                        description: step?.description || '',
                        code_line: step?.line_number || 0,
                    };
                } else {
                    result = { error: 'Player not available' };
                }
                break;
            }

            case 'clear_highlight': {
                if (cp) {
                    cp.clearVoiceHighlight();
                    result = { success: true };
                } else {
                    result = { error: 'Code panel not available' };
                }
                break;
            }

            default:
                result = { error: `Unknown function: ${name}` };
        }

        // Re-enable external notifications after player's notify() fires
        setTimeout(() => {
            if (player) player._suppressExternal = false;
        }, 50);

        this.client.sendFunctionResult(callId, result);
    }

    /* --- Transcript --- */
    _appendTranscript(role, text) {
        if (!text || !text.trim()) return;
        const entry = document.createElement('div');
        entry.className = `transcript-entry ${role}`;

        const label = document.createElement('div');
        label.className = 'role-label';
        label.textContent = role === 'agent' ? 'Tutor' : 'You';

        const content = document.createElement('div');
        content.className = 'transcript-text';
        content.textContent = text;

        entry.appendChild(label);
        entry.appendChild(content);
        this.transcriptEl.appendChild(entry);
        this.transcriptEl.scrollTop = this.transcriptEl.scrollHeight;
    }

    /* --- Cost tracking --- */
    _startAudioTimer() {
        this._audioSeconds = 0;
        this._audioTimer = setInterval(() => {
            this._audioSeconds++;
            this._updateCost();
        }, 1000);
    }

    _stopAudioTimer() {
        if (this._audioTimer) {
            clearInterval(this._audioTimer);
            this._audioTimer = null;
        }
    }

    _updateCost() {
        if (!this.client) return;
        const u = this.client.usage;

        // Text token costs
        const textCost = (u.inputTokens * COST_TEXT_INPUT) + (u.outputTokens * COST_TEXT_OUTPUT);

        // Audio costs — approximate 50/50 split of elapsed time
        const halfSec = this._audioSeconds / 2;
        const audioCost = (halfSec * COST_AUDIO_IN) + (halfSec * COST_AUDIO_OUT);

        const total = textCost + audioCost;
        this.costEl.textContent = `$${total.toFixed(3)}`;
    }

    /* --- Session logging --- */
    async _logSession() {
        if (!this.client) return;
        const problem = window.getSelectedProblem ? window.getSelectedProblem() : null;
        const duration = this.client.sessionStartTime
            ? (Date.now() - this.client.sessionStartTime) / 1000
            : 0;

        try {
            await fetch('/api/log-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    problem_id: problem?.name || '',
                    duration_seconds: Math.round(duration),
                    input_tokens: this.client.usage.inputTokens,
                    output_tokens: this.client.usage.outputTokens,
                    audio_seconds: this._audioSeconds,
                    estimated_cost: parseFloat(this.costEl.textContent.replace('$', '')),
                }),
            });
        } catch (err) {
            console.warn('Failed to log voice session:', err);
        }

        // Reset for next session
        this.client = null;
        this._audioSeconds = 0;
    }
}


/* ----------------------------------------------------------
   Initialize on DOM ready
   ---------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    window.voiceUI = new VoiceUI();
});
