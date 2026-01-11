import React, { useState, useRef, useEffect } from 'react';
import './AudioPlayer.css';

const AudioPlayer = ({ script, podcastId, topic }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [useBrowserTTS, setUseBrowserTTS] = useState(false);
    const [error, setError] = useState('');

    const audioRef = useRef(null);
    const synthRef = useRef(window.speechSynthesis);

    // Browser TTS functions
    const speakWithBrowserTTS = () => {
        if (!script) return;

        // Cancel any ongoing speech
        synthRef.current.cancel();

        // Clean script for TTS
        const cleanText = script
            .replace(/\[.*?\]/g, '')  // Remove section markers
            .replace(/\*.*?\*/g, '')  // Remove sound effects
            .replace(/[🎙️📚🌟✨🎉📖🔬🌍🎨🎯🚀💡🏆⭐🎧📅]/g, '');  // Remove emojis

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 0.9;  // Slightly slower for kids
        utterance.pitch = 1.1;  // Slightly higher pitch
        utterance.volume = 1.0;

        // Get kid-friendly voice if available
        const voices = synthRef.current.getVoices();
        const preferredVoice = voices.find(v =>
            v.name.includes('Google') ||
            v.name.includes('Female') ||
            v.name.includes('Samantha')
        );
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        utterance.onstart = () => {
            setIsPlaying(true);
            setIsPaused(false);
        };

        utterance.onend = () => {
            setIsPlaying(false);
            setIsPaused(false);
        };

        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            setError('Failed to play audio. Please try again.');
            setIsPlaying(false);
        };

        synthRef.current.speak(utterance);
    };

    const pauseBrowserTTS = () => {
        if (synthRef.current.speaking) {
            synthRef.current.pause();
            setIsPaused(true);
        }
    };

    const resumeBrowserTTS = () => {
        if (synthRef.current.paused) {
            synthRef.current.resume();
            setIsPaused(false);
        }
    };

    const stopBrowserTTS = () => {
        synthRef.current.cancel();
        setIsPlaying(false);
        setIsPaused(false);
    };

    // Server-side TTS functions
    const generateAudioFile = async () => {
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://localhost:8000/api/v1/podcasts/generate-audio', {
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
                setAudioUrl(`http://localhost:8000${data.audio_url}`);
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
            speakWithBrowserTTS();
        } else if (audioUrl) {
            playAudioFile();
        } else {
            await generateAudioFile();
        }
    };

    const handlePause = () => {
        if (useBrowserTTS) {
            pauseBrowserTTS();
        } else {
            pauseAudioFile();
        }
    };

    const handleResume = () => {
        if (useBrowserTTS) {
            resumeBrowserTTS();
        } else {
            playAudioFile();
        }
    };

    const handleStop = () => {
        if (useBrowserTTS) {
            stopBrowserTTS();
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
            synthRef.current.cancel();
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
                    <small>🔊 Using browser's built-in voice</small>
                </div>
            )}
        </div>
    );
};

export default AudioPlayer;
