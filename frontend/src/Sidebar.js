import React, { useState } from 'react';
import './Sidebar.css';

// Asegúrate de que onOpenSettings se desestructure de las props
function Sidebar({ chats, onSelectChat, onNewChat, onDeleteChat, currentChatId, onToggleSidebar, isExpanded, onOpenSettings }) {
  const [hoveredChatId, setHoveredChatId] = useState(null);

  // Función para simular el inicio de sesión genérico (mantenida si la necesitas, aunque el botón se eliminó)

  // Función para simular el inicio de sesión con Google
  const handleGoogleLogin = () => {
    console.log("Clic en Iniciar Sesión con Google");
    alert("¡Iniciar Sesión con Google clicado! Aquí iría la integración OAuth 2.0.");
  };

  return (
    <div className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* Botón de hamburguesa en el TOP del sidebar */}
      <div className="sidebar-header-top">
        <button className="hamburger-menu-button" onClick={onToggleSidebar}>
          {/* Un simple icono de hamburguesa SVG */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 18L20 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            <path d="M4 12L20 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            <path d="M4 6L20 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        {/* Solo muestra el texto "Financial Advisor Chatbot" si está expandido */}
        {isExpanded && <span className="sidebar-header-text">Financial Advisor Chatbot</span>}
      </div>

      {/* Todo este contenido se muestra solo si está expandido */}
      {isExpanded && (
        <>
          {/* NUEVA SECCIÓN: Botones de inicio de sesión */}
          <div className="login-buttons-container">
            {/* Solo el botón de Google */}
            <button className="login-google-button" onClick={handleGoogleLogin}>
              <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/768px-Google_%22G%22_logo.svg.png" alt="Google logo" className="google-logo" />
              Iniciar Sesión con Google
            </button>
          </div>
          {/* FIN NUEVA SECCIÓN */}

          <div className="new-chat-button-container">
            <button className="new-chat-button" onClick={onNewChat}>
              + Nuevo chat
            </button>
          </div>
          <div className="conversations-header">
            Conversaciones
          </div>
          <ul className="chat-list">
            {chats.map((chat) => (
              <li
                key={chat.id}
                className={`chat-item ${chat.id === currentChatId ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
                onMouseEnter={() => setHoveredChatId(chat.id)}
                onMouseLeave={() => setHoveredChatId(null)}
              >
                <div className="chat-title">{chat.title}</div>
                <div className="chat-actions">
                  {hoveredChatId === chat.id && (
                    <button
                      className="delete-chat-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteChat(chat.id);
                      }}
                    >
                      X
                    </button>
                  )}
                  {hoveredChatId !== chat.id && (
                    <div className="chat-last-message-time">
                      23m
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
          
          <div className="sidebar-footer">
            {/* Aquí el onClick para abrir el panel de configuración */}
            <div className="configuration-link" onClick={onOpenSettings}> {/* <--- CAMBIO CLAVE AQUÍ */}
              ⚙️ Configuración
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Sidebar;