'use client';

// In-Browser Audio Encoder: Converts MediaStream to pure standard PCM WAV (.wav)
export class WavRecorder {
    private audioContext: AudioContext | null = null;
    private mediaStream: MediaStream | null = null;
    private mediaStreamSource: MediaStreamAudioSourceNode | null = null;
    private scriptProcessor: ScriptProcessorNode | null = null;
    private gainNode: GainNode | null = null;
    private audioBuffers: Float32Array[] = [];

    async start() {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
        } });
        
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }
        
        this.mediaStreamSource = this.audioContext.createMediaStreamSource(this.mediaStream);

        // 4096 buffer size, 1 input channel, 1 output channel
        this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
        this.audioBuffers = [];

        this.scriptProcessor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            this.audioBuffers.push(new Float32Array(inputData));
        };

        this.mediaStreamSource.connect(this.scriptProcessor);
        
        // Connect to a GainNode with 0 volume to prevent acoustic feedback loop 
        // (which causes OS Echo Cancellation to mute the mic!), but keep it connected 
        // to destination so Chrome doesn't kill the script processor.
        this.gainNode = this.audioContext.createGain();
        this.gainNode.gain.value = 0.0001; 
        this.scriptProcessor.connect(this.gainNode);
        this.gainNode.connect(this.audioContext.destination);
    }

    async stop(): Promise<Blob> {
        return new Promise((resolve) => {
            if (this.scriptProcessor && this.mediaStream && this.audioContext) {
                this.scriptProcessor.disconnect();
                if (this.gainNode) this.gainNode.disconnect();
                
                this.mediaStream.getTracks().forEach(track => track.stop());

                const sampleRate = this.audioContext.sampleRate;
                const wavBlob = this.encodeWAV(this.audioBuffers, sampleRate);

                this.audioContext.close().then(() => resolve(wavBlob));
            } else {
                resolve(new Blob());
            }
        });
    }

    private encodeWAV(buffers: Float32Array[], sampleRate: number): Blob {
        let bufferLength = 0;
        let maxAmplitude = 0;
        
        for (let i = 0; i < buffers.length; i++) {
            bufferLength += buffers[i].length;
            for (let j = 0; j < buffers[i].length; j++) {
                maxAmplitude = Math.max(maxAmplitude, Math.abs(buffers[i][j]));
            }
        }

        const result = new Float32Array(bufferLength);
        let offset = 0;
        for (let i = 0; i < buffers.length; i++) {
            result.set(buffers[i], offset);
            offset += buffers[i].length;
        }

        const buffer = new ArrayBuffer(44 + result.length * 2);
        const view = new DataView(buffer);

        const writeString = (view: DataView, offset: number, string: string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + result.length * 2, true);
        writeString(view, 8, 'WAVE');
        writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true); // PCM encoding
        view.setUint16(22, 1, true); // 1 channel
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(view, 36, 'data');
        view.setUint32(40, result.length * 2, true);

        // Enhance volume strictly to 95% if quiet
        const gain = maxAmplitude > 0.05 ? 0.95 / maxAmplitude : 1.0;

        let writeOffset = 44;
        for (let i = 0; i < result.length; i++, writeOffset += 2) {
            let s = result[i] * gain;
            s = Math.max(-1, Math.min(1, s));
            view.setInt16(writeOffset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }

        return new Blob([view], { type: 'audio/wav' });
    }
}
