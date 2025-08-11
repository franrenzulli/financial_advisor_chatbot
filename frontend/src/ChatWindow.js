import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import './ChatWindow.css';
import vector2Image from './img/vector2.PNG';
import ReactMarkdown from 'react-markdown';

// --- COMPONENTE MODAL ---
function FeedbackModal({ isOpen, onClose, onSubmit, message }) {
    const [selectedOption, setSelectedOption] = useState('');
    const [otherDetails, setOtherDetails] = useState('');

    if (!isOpen) return null;

    const feedbackOptions = [
        "Información incorrecta",
        "No ha seguido las instrucciones",
        "Ofensiva o inapropiada",
        "Idioma incorrecto",
    ];

    const handleSubmit = () => {
        const details = selectedOption === 'Otra' ? otherDetails : selectedOption;
        
        if (details && details.trim()) {
            onSubmit(message, details);
            onClose();
        } else {
            alert("Por favor, selecciona una opción o escribe un detalle en 'Otra'.");
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <span className="close-button" onClick={onClose}>&times;</span>
                <h2>¿Qué problema has tenido?</h2>
                <p>Tus comentarios nos ayudan a mejorar la aplicación.</p>

                <ul className="feedback-options">
                    {feedbackOptions.map((option, index) => (
                        <li key={index} onClick={() => setSelectedOption(option)} className={selectedOption === option ? 'selected' : ''}>
                            {option}
                        </li>
                    ))}
                    <li onClick={() => setSelectedOption('Otra')} className={selectedOption === 'Otra' ? 'selected' : ''}>
                        Otra
                    </li>
                </ul>

                {selectedOption === 'Otra' && (
                    <textarea
                        className="feedback-textarea"
                        placeholder="Por favor, danos más detalles..."
                        value={otherDetails}
                        onChange={(e) => setOtherDetails(e.target.value)}
                        autoFocus
                    />
                )}

                <button className="send-feedback-button" onClick={handleSubmit}>Enviar Comentarios</button>
            </div>
        </div>
    );
}


function ChatWindow({ currentChat, onSendMessage }) {
    const [messageInput, setMessageInput] = useState('');
    const messagesEndRef = useRef(null);
    const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
    const [feedbackTarget, setFeedbackTarget] = useState(null);
    const [copyStatus, setCopyStatus] = useState({ copied: false, messageId: null });

    const suggestedNasdaqPrompts = [
        "¿Cuál es el precio actual del índice Nasdaq?",
        "¿Qué empresas importantes cotizan en el Nasdaq?",
        "¿Cómo ha rendido el Nasdaq en el último mes?",
        "Explícame la historia del Nasdaq."
    ];

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [currentChat?.messages]);

    const handleInputChange = (event) => {
        setMessageInput(event.target.value);
    };

    const handleSendMessage = () => {
        if (messageInput.trim()) {
            onSendMessage(messageInput);
            setMessageInput('');
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    };

    const handleSuggestedPromptClick = (promptText) => {
        onSendMessage(promptText);
    };

    const handleFeedbackClick = (message, feedbackType) => {
        setFeedbackTarget(message);
        if (feedbackType === 'dislike') {
            setIsFeedbackModalOpen(true);
        } else {
            submitFeedback(message, 'like', '');
        }
    };
    
    const submitFeedback = async (message, feedbackType, details = '') => {
        const userQuestion = currentChat.messages.findLast((m) => m.sender === 'user');
        
        if (!userQuestion) {
            console.error("No se encontró la pregunta del usuario para este feedback.");
            alert("No se pudo encontrar la pregunta original para enviar el feedback.");
            return;
        }

        const payload = {
            question: userQuestion.text,
            answer: message.text,
            chat_id: currentChat.id,
            feedback_type: feedbackType,
            feedback_details: details,
            retrieved_chunks: message.sources || [] // Incluir las fuentes si existen
        };

        try {
            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error('Error al enviar el feedback');
            }
            
            const result = await response.json();
            console.log("Feedback enviado con éxito:", result);
            alert(`Feedback '${feedbackType}' enviado. ¡Gracias!`);

        } catch (error) {
            console.error("Error en submitFeedback:", error);
            alert("Hubo un problema al enviar tu feedback.");
        }
    };

    const handleCopy = (messageText, messageId) => {
        navigator.clipboard.writeText(messageText)
            .then(() => {
                setCopyStatus({ copied: true, messageId });
                setTimeout(() => setCopyStatus({ copied: false, messageId: null }), 2000);
            })
            .catch(err => console.error("Error al copiar: ", err));
    };
    
    if (!currentChat) {
        return (
            <div className="chat-window empty-chat-window">
                <div className="empty-chat-content">
                    <p>Selecciona un chat existente a la izquierda o crea uno nuevo para comenzar a interactuar.</p>
                    <img src={vector2Image} alt="Asistente Virtual Original" className="empty-chat-image" />
                </div>
            </div>
        );
    }
    
    const showWelcomeMessage = currentChat.messages.length === 0;

    return (
        <div className="chat-window">
            <Header chatTitle={currentChat.title} />
            <div className="messages-container">
                {showWelcomeMessage && (
                    <div className="welcome-message-overlay">
                        <div className="welcome-content">
                            <h1>¡Hola! Soy tu asesor financiero virtual.</h1>
                            <p>Estoy aquí para ayudarte con tus preguntas y tareas. ¿En qué puedo asistirte hoy?</p>
                            <p>Escribe tu primer mensaje abajo para comenzar.</p>
                            <div className="suggested-prompts-container">
                                {suggestedNasdaqPrompts.map((prompt, index) => (
                                    <button
                                        key={index}
                                        className="suggested-prompt-box"
                                        onClick={() => handleSuggestedPromptClick(prompt)}
                                    >
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {!showWelcomeMessage && currentChat.messages.map((message, index) => {
                    const cleanedMessageText = message.text.trim();

                    return (
                        <div key={index} className={`message-bubble ${message.sender}`}>
                            {message.sender === 'bot' ? (
                                <ReactMarkdown>{cleanedMessageText}</ReactMarkdown>
                            ) : (
                                cleanedMessageText
                            )}

                            {/* --- CÓDIGO AÑADIDO PARA MOSTRAR LAS FUENTES --- */}
                            {message.sender === 'bot' && message.sources && message.sources.length > 0 && (
                                <div className="sources-container">
                                    <hr />
                                    <strong>🔍 Fuentes recuperadas:</strong>
                                    <ul>
                                        {message.sources.map((source, idx) => (
                                            <li key={idx}>{source.page_content}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            {/* --- FIN DEL CÓDIGO AÑADIDO --- */}

                            {message.sender === 'bot' && (
                                <div className="message-actions">
                                    <button className="action-button" onClick={() => handleFeedbackClick(message, 'like')}>👍</button>
                                    <button className="action-button" onClick={() => handleFeedbackClick(message, 'dislike')}>👎</button>
                                    <button className="action-button" onClick={() => handleCopy(message.text, index)}>
                                        {copyStatus.copied && copyStatus.messageId === index ? '✅' : '📋'}
                                    </button>
                                </div>
                            )}
                        </div>
                    );
                })}
                <div ref={messagesEndRef} />
            </div>
            <div className="message-input-area">
                <textarea
                    className="message-textarea"
                    placeholder="Escribe tu mensaje..."
                    value={messageInput}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    rows="1"
                />
                <button className="send-button" onClick={handleSendMessage}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
            <div className="input-hint">
                Presiona Enter para envío; Shift + Enter para mas líneas
            </div>

            <FeedbackModal
                isOpen={isFeedbackModalOpen}
                onClose={() => setIsFeedbackModalOpen(false)}
                onSubmit={(message, details) => submitFeedback(message, 'dislike', details)}
                message={feedbackTarget}
            />
        </div>
    );
}

export default ChatWindow;