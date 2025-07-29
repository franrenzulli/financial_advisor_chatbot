import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // Importamos Router
import Sidebar from './Sidebar'; // Estos son componentes de la página de chat
import ChatWindow from './ChatWindow';
import SettingsPanel from './SettingsPanel'; // El panel de configuración se muestra sobre cualquier ruta
import HomePage from './HomePage'; // Importamos la nueva HomePage
import './App.css';

// Componente Wrapper para la página del Chat
// Este componente encapsula Sidebar y ChatWindow, que siempre van juntos.
function ChatPage({
  chats, currentChatId, isSidebarExpanded,
  handleSelectChat, handleNewChat, handleDeleteChat,
  handleSendMessage, toggleSidebarExpansion, openSettingsPanel
}) {
  const currentChat = chats.find(chat => chat.id === currentChatId); // currentChat se deriva aquí, no se pasa como prop

  return (
    <div className="app-container">
      <Sidebar
        chats={chats}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        currentChatId={currentChatId}
        onToggleSidebar={toggleSidebarExpansion}
        isExpanded={isSidebarExpanded}
        onOpenSettings={openSettingsPanel}
      />
      <ChatWindow
        currentChat={currentChat} // currentChat se pasa aquí
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}


function App() {
  const [chats, setChats] = useState([
    { id: '1', title: 'Mi primer chat', messages: [] },
    { id: '2', title: 'Ayuda con Javascript', messages: [{ text: 'Necesito ayuda con Javascript.', sender: 'user' }] },
    { id: '3', title: 'Consejos de diseño', messages: [{ text: '¿Qué quieres crear en este cuadro?', sender: 'user' }] },
  ]);
  const [currentChatId, setCurrentChatId] = useState('1');
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);

  useEffect(() => {
    document.body.className = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleSelectChat = (chatId) => {
    setCurrentChatId(chatId);
  };

  const handleNewChat = () => {
    const newChatId = String(Date.now());
    const newChat = {
      id: newChatId,
      title: 'Nuevo Chat ' + newChatId.substring(newChatId.length - 4),
      messages: [],
    };
    setChats([...chats, newChat]);
    setCurrentChatId(newChatId);
    setIsSidebarExpanded(true);
  };

  const handleDeleteChat = (chatIdToDelete) => {
    const updatedChats = chats.filter(chat => chat.id !== chatIdToDelete);
    setChats(updatedChats);

    if (currentChatId === chatIdToDelete || updatedChats.length === 0) {
      setCurrentChatId(updatedChats.length > 0 ? updatedChats[0].id : null);
    }
    if (updatedChats.length === 0) {
      setIsSidebarExpanded(true);
    }
  };

  const handleSendMessage = async (messageText) => {
    const currentChatForSend = chats.find(chat => chat.id === currentChatId);
    if (!currentChatForSend) return;

    const newUserMessage = { text: messageText, sender: 'user' };
    const updatedUserMessages = [...currentChatForSend.messages, newUserMessage];

    // Mostrar mensaje del usuario de inmediato
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === currentChatId
          ? { ...chat, messages: updatedUserMessages }
          : chat
      )
    );

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: messageText,
          chat_history: updatedUserMessages.map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.text,
          })),
        }),
      });

      const data = await response.json();

      const newMessages = [];
      if (data.answer) {
        newMessages.push({ text: data.answer, sender: 'bot' });
      }

      if (data.retrieved_chunks && data.retrieved_chunks.length > 0) {
        newMessages.push({
          text: `🔍 *Fuentes recuperadas:*\n\n${data.retrieved_chunks.map((c, i) => `Chunk ${i + 1}:\n${c}`).join('\n\n')}`,
          sender: 'bot',
        });
      }

      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === currentChatId
            ? { ...chat, messages: [...updatedUserMessages, ...newMessages] }
            : chat
        )
      );
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === currentChatId
            ? {
                ...chat,
                messages: [
                  ...updatedUserMessages,
                  { text: '❌ Hubo un error al obtener respuesta del servidor.', sender: 'bot' },
                ],
              }
            : chat
        )
      );
    }
  };

  const toggleSidebarExpansion = () => {
    setIsSidebarExpanded(!isSidebarExpanded);
  };

  const openSettingsPanel = () => {
    setShowSettingsPanel(true);
  };

  const closeSettingsPanel = () => {
    setShowSettingsPanel(false);
  };

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <Router> {/* Envolvemos toda la aplicación en BrowserRouter */}
      <Routes> {/* Definimos las diferentes rutas */}
        <Route path="/" element={<HomePage />} /> {/* Página de Inicio */}
        <Route
          path="/chat"
          element={
            <ChatPage
              chats={chats}
              currentChatId={currentChatId}
              isSidebarExpanded={isSidebarExpanded}
              handleSelectChat={handleSelectChat}
              handleNewChat={handleNewChat}
              handleDeleteChat={handleDeleteChat}
              handleSendMessage={handleSendMessage}
              toggleSidebarExpansion={toggleSidebarExpansion}
              openSettingsPanel={openSettingsPanel}
            />
          }
        /> {/* Página del Chat */}
      </Routes>

      {/* El panel de configuración se muestra sobre CUALQUIER ruta si está activo */}
      {showSettingsPanel && (
        <SettingsPanel
          onClose={closeSettingsPanel}
          currentTheme={theme}
          onToggleTheme={toggleTheme}
        />
      )}
    </Router>
  );
}

export default App;