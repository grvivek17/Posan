import { useState, useRef, useEffect } from 'react';
import {
    isSpeechRecognitionAvailable,
    requestSpeechPermission,
    startListening,
} from '../../services/voiceService';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onRecordingComplete, isProcessing = false }) => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [available, setAvailable] = useState(true);
    const listenerRef = useRef(null);

    useEffect(() => {
        // Check availability on mount
        isSpeechRecognitionAvailable().then(setAvailable);

        return () => {
            // Cleanup: stop listening on unmount
            if (listenerRef.current) {
                listenerRef.current.stop();
                listenerRef.current = null;
            }
        };
    }, []);

    const handleStartListening = async () => {
        if (!available) {
            alert('Speech recognition is not available on this device.');
            return;
        }

        // Request permission (native platforms need this)
        const granted = await requestSpeechPermission();
        if (!granted) {
            alert('Microphone access denied. Please allow microphone access in your device settings.');
            return;
        }

        setTranscript('');
        setIsListening(true);

        listenerRef.current = startListening({
            language: 'en-US',
            partialResults: true,
            onPartialResult: (text) => setTranscript(text),
            onFinalResult: (text) => {
                console.log('Final transcript:', text);
                setTranscript(text);
                setIsListening(false);
                listenerRef.current = null;
                onRecordingComplete(text);
            },
            onError: (err) => {
                console.error('Speech recognition error:', err);
                setIsListening(false);
                listenerRef.current = null;
                alert(err.message || 'Speech recognition error. Please try again.');
            },
            onEnd: () => {
                setIsListening(false);
            },
        });
    };

    const handleStopListening = () => {
        if (listenerRef.current) {
            listenerRef.current.stop();
            listenerRef.current = null;
        }
        setIsListening(false);
    };

    return (
        <div className="voice-recorder">
            {!isListening && !isProcessing && (
                <button
                    className="record-btn start"
                    onClick={handleStartListening}
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
                        onClick={handleStopListening}
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
