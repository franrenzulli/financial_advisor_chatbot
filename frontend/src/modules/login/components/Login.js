// src/Login.js
import { auth, provider, signInWithPopup } from "../../../firebase";

function Login({ setUser }) {
  const handleLogin = () => {
    signInWithPopup(auth, provider)
      .then((result) => {
        const user = result.user;
        setUser({
          name: user.displayName,
          email: user.email,
          photo: user.photoURL,
        });
      })
      .catch((error) => {
        console.error("Error al iniciar sesión:", error);
      });
  };

  return (
    <button className="login-google-button" onClick={handleLogin}>
      <img
        src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/768px-Google_%22G%22_logo.svg.png"
        alt="Google logo"
        className="google-logo"
      />
      Iniciar Sesión con Google
    </button>
  );
}

export default Login;
