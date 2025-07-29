import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';
import vectorImage from './img/vector.jpg'; // Importa tu imagen desde src/img/

function HomePage() {
  return (
    <div className="homepage-container">
      {/* Mitad Izquierda: Imagen Grande */}
      <div className="homepage-left">
        <img src={vectorImage} alt="Asesor Financiero" className="homepage-image" />
      </div>

      {/* Mitad Derecha: Mensaje y Botón */}
      <div className="homepage-right">
        <div className="message-area"> {/* Área azul para el mensaje */}
          <h1>Bienvenido a tu Asesor Financiero Virtual</h1>
          <p>Tu compañero inteligente para gestionar tus finanzas y responder a tus preguntas.</p>
        </div>
        {/* Botón Rojo para ir al chat */}
        <Link to="/chat" className="start-chat-button">
          Comenzar Chat
        </Link>
      </div>
    </div>
  );
}

export default HomePage;