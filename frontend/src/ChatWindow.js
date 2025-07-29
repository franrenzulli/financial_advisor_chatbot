import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import './ChatWindow.css';
import vector2Image from './img/vector2.PNG';

function ChatWindow({ currentChat, onSendMessage }) {
  const [messageInput, setMessageInput] = useState('');
  const messagesEndRef = useRef(null);

  // Prompts sugeridos sobre el Nasdaq
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

  // NUEVA FUNCIÓN: Maneja el clic en un prompt sugerido
  const handleSuggestedPromptClick = (promptText) => {
    onSendMessage(promptText); // Envía el texto del prompt como un mensaje
  };

  const handleFeedback = (messageId, type) => {
    console.log(`Mensaje ${messageId}: ${type} clicado`);
    alert(`Feedback "${type}" enviado para el mensaje.`);
  };

  const handleCopy = (messageText) => {
    navigator.clipboard.writeText(messageText)
      .then(() => console.log("Texto copiado!"))
      .catch(err => console.error("Error al copiar: ", err));
    alert("Mensaje copiado al portapapeles.");
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

              {/* NUEVA SECCIÓN: Prompts sugeridos */}
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
          const cleanedMessageText = message.text
            .replace(/&nbsp;/g, ' ')
            .replace(/\s\s+/g, ' ')
            .trim();

          return (
            <div key={index} className={`message-bubble ${message.sender}`}>
              {cleanedMessageText}
              {message.sender === 'bot' && (
                <div className="message-actions">
                  <button className="action-button" onClick={() => handleFeedback(index, 'like')}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h3"></path>
                    </svg>
                  </button>
                  <button className="action-button" onClick={() => handleFeedback(index, 'dislike')}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zM17 2H20a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-3"></path>
                    </svg>
                  </button>
                  <button className="action-button" onClick={() => handleCopy(message.text)}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
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
    </div>
  );
}

export default ChatWindow;