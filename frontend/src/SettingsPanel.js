import "./SettingsPanel.css"; // Crearás este archivo CSS a continuación
import { auth, signOut } from "./firebase";

function SettingsPanel({ onClose, currentTheme, onToggleTheme, user, setUser }) {
  const handleLogout = () => {
    signOut(auth)
      .then(() => {
        setUser(null)
        onClose();
      })
      .catch((err) => console.error("Error al cerrar sesión:", err));
  };
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
                checked={currentTheme === "dark"}
                onChange={onToggleTheme}
              />
              <span className="slider round"></span>
            </label>
          </div>
          {user && (
            <div>
              <button className="signOut-button" onClick={handleLogout}>
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
