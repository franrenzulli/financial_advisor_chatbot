import React from 'react';
import './Header.css';
import userIcon from './img/user.svg';
// No necesitas el SVG de la tuerca aquí, ya que el icono del usuario la reemplaza.

function Header({ chatTitle, user, onOpenSettings }) {
  return (
    <div className="header">
      <div className="chat-title-display">
        {chatTitle}
      </div>
      {/*
        Al hacer clic en la foto de perfil o en el ícono de usuario,
        se abre el panel de configuración.
      */}
      <div className="settings-icon" onClick={onOpenSettings}>
        {user && user.photo ? (
          // Si el usuario está logueado y tiene foto, se muestra
          <img src={user.photo} alt="User Profile" className="user-profile-pic" />
        ) : (
          // Si no hay usuario, se muestra el ícono de usuario genérico
          // ¡Y este ícono es el que al hacer clic abrirá la configuración!
          <img src={userIcon} alt="User Icon" className="user-icon" />
        )}
      </div>
    </div>
  );
}

export default Header;