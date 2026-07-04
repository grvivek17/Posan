import React, { useState, useRef, useEffect } from 'react';
import {
    speak,
    stopSpeaking,
    pauseSpeaking,
    resumeSpeaking,
    isNative,
} from '../../services/voiceService';
import './AudioPlayer.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const API_HOST = API_BASE.replace(/\/api\/v1$/, '');

const AudioPlayer = ({ script, podcastId, topic }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [useBrowserTTS, setUseBrowserTTS] = useState(false);
    const [error, setError] = useState('');

    const audioRef = useRef(null);

    // Clean script for TTS
    const cleanScript = (text) => {
        if (!text) return '';
        return text
            .replace(/\[.*?\]/g, '')
            .replace(/\*.*?\*/g, '')
            .replace(/[🎙️📚🌟✨🎉📖🔬🌍🎨🎯🚀💡🏆⭐🎧📅]/g, '');
    };

    // Platform-aware TTS (uses native on Android, browser on web)
    const speakWithTTS = () => {
        if (!script) return;
        const text = cleanScript(script);

        speak(text, {
            rate: 0.9,
            pitch: 1.1,
            volume: 1.0,
            onStart: () => {
                setIsPlaying(true);
                setIsPaused(false);
            },
            onEnd: () => {
                setIsPlaying(false);
                setIsPaused(false);
            },
            onError: (e) => {
                console.error('TTS error:', e);
                setError('Failed to play audio. Please try again.');
                setIsPlaying(false);
            },
        });
    };

    const pauseTTS = () => {
        if (isNative) {
            // Native TTS has no pause; stop it instead
            stopSpeaking();
            setIsPlaying(false);
            setIsPaused(false);
        } else {
            pauseSpeaking();
            setIsPaused(true);
        }
    };

    const resumeTTS = () => {
        if (isNative) {
            // Re-speak from beginning on native (no pause support)
            speakWithTTS();
        } else {
            resumeSpeaking();
            setIsPaused(false);
        }
    };

    const stopTTS = () => {
        stopSpeaking();
        setIsPlaying(false);
        setIsPaused(false);
    };

    // Server-side TTS functions
    const generateAudioFile = async () => {
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_BASE}/podcasts/generate-audio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    text: script,
                    podcast_id: podcastId || Date.now().toString()
                })
            });

            const data = await response.json();

            if (data.success && data.audio_url) {
                setAudioUrl(`${API_HOST}${data.audio_url}`);
                setUseBrowserTTS(false);
            } else {
                // Fallback to browser TTS
                console.log('Using browser TTS fallback');
                setUseBrowserTTS(true);
            }
        } catch (err) {
            console.error('Error generating audio:', err);
            setUseBrowserTTS(true);
        } finally {
            setLoading(false);
        }
    };

    const playAudioFile = () => {
        if (audioRef.current) {
            audioRef.current.play();
            setIsPlaying(true);
            setIsPaused(false);
        }
    };

    const pauseAudioFile = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            setIsPaused(true);
        }
    };

    const stopAudioFile = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
            setIsPlaying(false);
            setIsPaused(false);
        }
    };

    // Main play function
    const handlePlay = async () => {
        if (useBrowserTTS) {
            speakWithTTS();
        } else if (audioUrl) {
            playAudioFile();
        } else {
            await generateAudioFile();
        }
    };

    const handlePause = () => {
        if (useBrowserTTS) {
            pauseTTS();
        } else {
            pauseAudioFile();
        }
    };

    const handleResume = () => {
        if (useBrowserTTS) {
            resumeTTS();
        } else {
            playAudioFile();
        }
    };

    const handleStop = () => {
        if (useBrowserTTS) {
            stopTTS();
        } else {
            stopAudioFile();
        }
    };

    // Auto-play audio file when URL is available
    useEffect(() => {
        if (audioUrl && audioRef.current) {
            playAudioFile();
        }
    }, [audioUrl]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopSpeaking();
            if (audioRef.current) {
                audioRef.current.pause();
            }
        };
    }, []);

    return (
        <div className="audio-player">
            <div className="audio-player-header">
                <div className="audio-icon">🎧</div>
                <div className="audio-info">
                    <h4>Listen to Podcast</h4>
                    <p>{topic || 'Your Podcast'}</p>
                </div>
            </div>

            {error && (
                <div className="audio-error">
                    <span>⚠️</span> {error}
                </div>
            )}

            {loading && (
                <div className="audio-loading">
                    <div className="spinner-small"></div>
                    <span>Generating audio...</span>
                </div>
            )}

            {/* Hidden audio element for file playback */}
            {audioUrl && (
                <audio
                    ref={audioRef}
                    src={audioUrl}
                    onEnded={() => {
                        setIsPlaying(false);
                        setIsPaused(false);
                    }}
                    onError={() => {
                        setError('Failed to load audio file');
                        setUseBrowserTTS(true);
                    }}
                />
            )}

            <div className="audio-controls">
                {!isPlaying ? (
                    <button
                        className="audio-btn play-btn"
                        onClick={handlePlay}
                        disabled={loading}
                    >
                        ▶️ Play
                    </button>
                ) : isPaused ? (
                    <button
                        className="audio-btn resume-btn"
                        onClick={handleResume}
                    >
                        ▶️ Resume
                    </button>
                ) : (
                    <button
                        className="audio-btn pause-btn"
                        onClick={handlePause}
                    >
                        ⏸️ Pause
                    </button>
                )}

                {isPlaying && (
                    <button
                        className="audio-btn stop-btn"
                        onClick={handleStop}
                    >
                        ⏹️ Stop
                    </button>
                )}
            </div>

            {useBrowserTTS && (
                <div className="tts-info">
                    <small>{isNative ? '🔊 Using device voice' : '🔊 Using browser\'s built-in voice'}</small>
                </div>
            )}
        </div>
    );
};

export default AudioPlayer;
