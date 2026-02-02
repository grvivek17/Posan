import { useState, useRef, useEffect } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onRecordingComplete, isProcessing = false }) => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const recognitionRef = useRef(null);

    useEffect(() => {
        // Check if browser supports Speech Recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcriptPiece = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcriptPiece;
                    } else {
                        interimTranscript += transcriptPiece;
                    }
                }

                setTranscript(finalTranscript || interimTranscript);

                // If we got a final result, process it
                if (finalTranscript) {
                    console.log('Final transcript:', finalTranscript);
                    // Send as text to backend (no audio file needed!)
                    onRecordingComplete(finalTranscript);
                    setIsListening(false);
                }
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsListening(false);

                if (event.error === 'no-speech') {
                    alert('No speech detected. Please try again.');
                } else if (event.error === 'not-allowed') {
                    alert('Microphone access denied. Please allow microphone access.');
                } else {
                    alert('Speech recognition error. Please try again.');
                }
            };

            recognition.onend = () => {
                setIsListening(false);
            };

            recognitionRef.current = recognition;
        }

        return () => {
            if (recognitionRef.current) {
                try {
                    recognitionRef.current.stop();
                } catch (e) {
                    // Ignore errors on cleanup
                }
            }
        };
    }, [onRecordingComplete]);

    const startListening = () => {
        if (!recognitionRef.current) {
            alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        setTranscript('');
        setIsListening(true);
        try {
            recognitionRef.current.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            setIsListening(false);
        }
    };

    const stopListening = () => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    };

    return (
        <div className="voice-recorder">
            {!isListening && !isProcessing && (
                <button
                    className="record-btn start"
                    onClick={startListening}
                    title="Click to start speaking"
                >
                    🎤 Start Speaking
                </button>
            )}

            {isListening && (
                <div className="recording-controls">
                    <div className="recording-indicator">
                        <span className="pulse-dot"></span>
                        <span className="recording-text">Listening...</span>
                    </div>
                    {transcript && (
                        <div className="live-transcript">
                            "{transcript}"
                        </div>
                    )}
                    <button
                        className="record-btn stop"
                        onClick={stopListening}
                    >
                        ⏹️ Stop
                    </button>
                </div>
            )}

            {isProcessing && (
                <div className="processing-indicator">
                    <div className="spinner"></div>
                    <span>Calculating...</span>
                </div>
            )}
        </div>
    );
};

export default VoiceRecorder;
