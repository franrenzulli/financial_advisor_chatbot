import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import SettingsPanel from './SettingsPanel';
import HomePage from './HomePage';
import './App.css';

// Componente Wrapper para la página del Chat
function ChatPage({
  chats, currentChatId, isSidebarExpanded,
  handleSelectChat, handleNewChat, handleDeleteChat,
  handleSendMessage, toggleSidebarExpansion, openSettingsPanel,
  user, setUser
}) {
  const currentChat = chats.find(chat => chat.id === currentChatId);

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
        user={user}
        setUser={setUser}
      />
      <ChatWindow
        currentChat={currentChat}
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
  const [user, setUser] = useState(null);

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

  // --- ESTA ES LA FUNCIÓN CORREGIDA ---
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Creamos un solo mensaje para el bot que contiene la respuesta Y las fuentes.
      const newBotMessage = {
          text: data.answer || "No se recibió respuesta.",
          sender: 'bot',
          // Guardamos el array de chunks en una nueva propiedad 'sources'
          sources: data.retrieved_chunks || [] 
      };

      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === currentChatId
            ? { ...chat, messages: [...updatedUserMessages, newBotMessage] }
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
                  { text: '❌ Hubo un error al obtener respuesta del servidor.', sender: 'bot', sources: [] },
                ],
              }
            : chat
        )
      );
    }
  };
  // --- FIN DE LA FUNCIÓN CORREGIDA ---

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
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
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
              user={user}
              setUser={setUser}
            />
          }
        />
      </Routes>

      {showSettingsPanel && (
        <SettingsPanel
          onClose={closeSettingsPanel}
          currentTheme={theme}
          onToggleTheme={toggleTheme}
          user={user}
          setUser={setUser}
        />
      )}
    </Router>
  );
}

export default App;