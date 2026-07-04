/**
 * Platform-aware voice service abstraction.
 *
 * Uses native Capacitor plugins on Android/iOS (where the Web Speech API
 * is unavailable inside a WebView), and falls back to the browser
 * Web Speech API when running in a regular browser.
 */
import { Capacitor } from '@capacitor/core';
import { TextToSpeech } from '@capacitor-community/text-to-speech';
import { SpeechRecognition } from '@capacitor-community/speech-recognition';

const isNative = Capacitor.isNativePlatform();

/* ─── Text-to-Speech ─── */

/**
 * Speak the given text using the best available TTS engine.
 * @param {string} text
 * @param {object} [opts]
 * @param {number} [opts.rate=0.9]
 * @param {number} [opts.pitch=1.1]
 * @param {number} [opts.volume=1.0]
 * @param {() => void} [opts.onStart]
 * @param {() => void} [opts.onEnd]
 * @param {(err: any) => void} [opts.onError]
 */
export async function speak(text, opts = {}) {
    const { rate = 0.9, pitch = 1.1, volume = 1.0, onStart, onEnd, onError } = opts;

    if (isNative) {
        try {
            onStart?.();
            await TextToSpeech.speak({
                text,
                lang: 'en-US',
                rate,
                pitch,
                volume,
                category: 'playback',
            });
            onEnd?.();
        } catch (err) {
            console.error('Native TTS error:', err);
            onError?.(err);
        }
    } else if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = rate;
        utterance.pitch = pitch;
        utterance.volume = volume;

        const voices = window.speechSynthesis.getVoices();
        const friendly = voices.find(
            (v) =>
                v.name.includes('Female') ||
                v.name.includes('Jenny') ||
                v.name.includes('Samantha') ||
                v.name.includes('Google') ||
                v.lang.startsWith('en')
        );
        if (friendly) utterance.voice = friendly;

        utterance.onstart = () => onStart?.();
        utterance.onend = () => onEnd?.();
        utterance.onerror = (e) => onError?.(e);

        window.speechSynthesis.speak(utterance);
    } else {
        console.warn('No TTS engine available');
        onError?.(new Error('TTS not available'));
    }
}

/** Stop any ongoing speech. */
export async function stopSpeaking() {
    if (isNative) {
        try {
            await TextToSpeech.stop();
        } catch {
            // ignore
        }
    } else if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
}

/** Pause browser TTS (native TTS has no pause – we just stop). */
export function pauseSpeaking() {
    if (isNative) {
        // Native plugin has no pause; caller should stop + re-speak
        return;
    }
    if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
    }
}

/** Resume browser TTS. */
export function resumeSpeaking() {
    if (isNative) return;
    if ('speechSynthesis' in window && window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
    }
}

/** Check whether TTS is currently speaking (browser only – native resolves on completion). */
export function isSpeakingNow() {
    if (isNative) return false; // native speak() is async, not trackable this way
    return 'speechSynthesis' in window && window.speechSynthesis.speaking;
}

/* ─── Speech Recognition ─── */

/**
 * Check whether speech recognition is available on this platform.
 */
export async function isSpeechRecognitionAvailable() {
    if (isNative) {
        try {
            const { available } = await SpeechRecognition.available();
            return available;
        } catch {
            return false;
        }
    }
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

/**
 * Request microphone / speech-recognition permissions (native only).
 * Returns true if granted.
 */
export async function requestSpeechPermission() {
    if (!isNative) return true; // browser handles its own permission prompt
    try {
        const status = await SpeechRecognition.requestPermissions();
        return status.speechRecognition === 'granted';
    } catch {
        return false;
    }
}

/**
 * Start listening and return the final transcript.
 *
 * On native platforms this returns a Promise<string> that resolves with the
 * best match.  On web it sets up the Web Speech API and calls the provided
 * callbacks for interim / final results.
 *
 * @param {object} opts
 * @param {string}   [opts.language='en-US']
 * @param {boolean}  [opts.partialResults=true]
 * @param {(text: string) => void} [opts.onPartialResult]  interim transcript
 * @param {(text: string) => void} opts.onFinalResult      final transcript
 * @param {(err: any) => void}     [opts.onError]
 * @param {() => void}             [opts.onEnd]
 * @returns {{ stop: () => void }}  call stop() to cancel listening
 */
export function startListening(opts = {}) {
    const {
        language = 'en-US',
        partialResults = true,
        onPartialResult,
        onFinalResult,
        onError,
        onEnd,
    } = opts;

    if (isNative) {
        return _startNativeListening({ language, partialResults, onPartialResult, onFinalResult, onError, onEnd });
    }
    return _startWebListening({ language, partialResults, onPartialResult, onFinalResult, onError, onEnd });
}

/* --- native impl --- */
function _startNativeListening({ language, partialResults, onPartialResult, onFinalResult, onError, onEnd }) {
    let stopped = false;
    let partialListener = null;

    (async () => {
        try {
            if (partialResults) {
                partialListener = await SpeechRecognition.addListener('partialResults', (data) => {
                    if (stopped) return;
                    const text = data.matches?.[0] || '';
                    onPartialResult?.(text);
                });
            }

            const result = await SpeechRecognition.start({
                language,
                maxResults: 3,
                partialResults,
                popup: false,
            });

            if (!stopped) {
                const transcript = result.matches?.[0] || '';
                onFinalResult?.(transcript);
            }
        } catch (err) {
            if (!stopped) {
                console.error('Native speech recognition error:', err);
                onError?.(err);
            }
        } finally {
            partialListener?.remove?.();
            if (!stopped) onEnd?.();
        }
    })();

    return {
        stop: () => {
            stopped = true;
            SpeechRecognition.stop().catch(() => {});
            partialListener?.remove?.();
        },
    };
}

/* --- web impl --- */
function _startWebListening({ language, onPartialResult, onFinalResult, onError, onEnd }) {
    const SpeechRecClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecClass) {
        onError?.(new Error('Speech recognition not supported in this browser.'));
        return { stop: () => {} };
    }

    const recognition = new SpeechRecClass();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onresult = (event) => {
        let interim = '';
        let final = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const piece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                final += piece;
            } else {
                interim += piece;
            }
        }
        if (interim) onPartialResult?.(interim);
        if (final) onFinalResult?.(final);
    };

    recognition.onerror = (event) => {
        const msg =
            event.error === 'no-speech'
                ? 'No speech detected. Please try again.'
                : event.error === 'not-allowed'
                ? 'Microphone access denied. Please allow microphone access.'
                : 'Speech recognition error. Please try again.';
        onError?.(new Error(msg));
    };

    recognition.onend = () => onEnd?.();

    try {
        recognition.start();
    } catch (err) {
        onError?.(err);
    }

    return {
        stop: () => {
            try { recognition.stop(); } catch { /* ignore */ }
        },
    };
}

export { isNative };
