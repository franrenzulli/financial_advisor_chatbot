import React from 'react';
import './SettingsPanel.css'; // Crearás este archivo CSS a continuación

function SettingsPanel({ onClose, currentTheme, onToggleTheme }) {
  return (
    <div className="settings-panel-overlay">
      <div className="settings-panel">
        <div className="settings-panel-header">
          <h2>Configuración</h2>
          <button className="close-button" onClick={onClose}>
            &times; {/* Carácter de 'x' para cerrar */}
          </button>
        </div>
        <div className="settings-panel-body">
          <div className="setting-item">
            <span>Modo Oscuro</span>
            <label className="switch">
              <input
                type="checkbox"
                checked={currentTheme === 'dark'}
                onChange={onToggleTheme}
              />
              <span className="slider round"></span>
            </label>
          </div>
          {/* Puedes añadir más opciones de configuración aquí */}
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;