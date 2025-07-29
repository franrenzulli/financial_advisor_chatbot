import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Esto es opcional, si no tienes un index.css, puedes quitarlo.
import App from './App'; // Asegúrate de que esta ruta sea correcta

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);