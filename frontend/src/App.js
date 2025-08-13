import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import SettingsPanel from './SettingsPanel';
import HomePage from './HomePage';
import './App.css';
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebase";

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
        user={user}
        onOpenSettings={openSettingsPanel}
        onToggleSidebar={toggleSidebarExpansion}
      />
    </div>
  );
}

// ✅ 1. Definimos los chats de ejemplo fuera del componente
const exampleChats = [
  { id: '1', title: 'Mi primer chat', messages: [] },
];

function App() {
  // ✅ 2. Inicializamos el estado con los chats de ejemplo
  const [chats, setChats] = useState(exampleChats);
  const [currentChatId, setCurrentChatId] = useState('1');
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  // useEffect para la autenticación
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        localStorage.setItem('firebaseUserId', user.uid);
        setUser({
          uid: user.uid,
          name: user.displayName,
          email: user.email,
          photo: user.photoURL,
        });
        // La carga de chats reales se maneja en el siguiente useEffect
      } else {
        localStorage.removeItem('firebaseUserId');
        setUser(null);
        // ✅ 3. RESTAURAMOS LOS CHATS DE EJEMPLO AL CERRAR SESIÓN
        setChats(exampleChats);
        setCurrentChatId(exampleChats.length > 0 ? exampleChats[0].id : null);
      }
      setLoadingUser(false);
    });
    return () => unsubscribe();
  }, []);

  // useEffect para cargar los chats del usuario logueado
  useEffect(() => {
    if (!user) {
      return; // Si no hay usuario, no hacemos nada (se quedan los de ejemplo)
    }

    const fetchChats = async () => {
      try {
        const response = await fetch(`http://localhost:8000/chats/${user.uid}`);
        if (!response.ok) {
          throw new Error('Error al cargar los chats del servidor');
        }
        const userChats = await response.json();
        setChats(userChats);
        if (userChats.length > 0) {
          setCurrentChatId(userChats[0].id);
        } else {
          // Si el usuario no tiene chats, no seleccionamos ninguno
          setCurrentChatId(null);
        }
      } catch (error) {
        console.error("Error fetching chats:", error);
        // En caso de error, podríamos dejar los chats de ejemplo o mostrar un estado de error
        setChats(exampleChats);
      }
    };

    fetchChats();
  }, [user]); // Se ejecuta cada vez que el objeto 'user' cambia

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
  
  const handleNewChat = async () => {
    if (!user) {
      alert("Por favor, inicia sesión para crear un nuevo chat.");
      return;
    }

    const newChatTitle = 'Nuevo Chat ' + String(Date.now()).slice(-4);

    try {
      const response = await fetch('http://localhost:8000/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.uid,
          email: user.email,
          name: user.name,
          title: newChatTitle,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Falló la creación del chat en el servidor');
      }

      const newChatFromDB = await response.json();
      
      setChats(prevChats => [newChatFromDB, ...prevChats]);
      setCurrentChatId(newChatFromDB.id);
      setIsSidebarExpanded(true);

    } catch (error) {
      console.error("Error al crear el nuevo chat:", error);
      alert(`Hubo un error al crear el chat: ${error.message}`);
    }
  };

  const handleDeleteChat = async (chatIdToDelete) => {
    try {
        const response = await fetch(`http://localhost:8000/chats/${chatIdToDelete}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Falló el borrado del chat en el servidor');
        }

        const updatedChats = chats.filter(chat => chat.id !== chatIdToDelete);
        setChats(updatedChats);

        if (currentChatId === chatIdToDelete) {
            setCurrentChatId(updatedChats.length > 0 ? updatedChats[0].id : null);
        }

    } catch (error) {
        console.error("Error al borrar el chat:", error);
        alert(`Hubo un error al borrar el chat: ${error.message}`);
    }
  };

  const handleSendMessage = async (messageText) => {
    const currentChatForSend = chats.find(chat => chat.id === currentChatId);
    if (!currentChatForSend) return;

    const newUserMessage = { text: messageText, sender: 'user' };

    // Actualización optimista de la UI
    const updatedChats = chats.map(chat =>
      chat.id === currentChatId
        ? { ...chat, messages: [...chat.messages, newUserMessage] }
        : chat
    );
    setChats(updatedChats);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: messageText,
          chat_history: currentChatForSend.messages.map(msg => ({
            role: msg.sender,
            content: msg.text,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const newBotMessage = {
        text: data.answer || "No se recibió respuesta.",
        sender: 'bot',
        sources: data.retrieved_chunks || []
      };

      // Actualizar el estado con la respuesta del bot
      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === currentChatId
            ? { ...chat, messages: [...chat.messages, newBotMessage] }
            : chat
        )
      );
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      // Opcional: manejar el estado de error en la UI
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

  if (loadingUser) {
    return <div className="loading-state">Cargando usuario...</div>;
  }

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
