// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDohbctztJpr6jhJFqWU2c6g5S1CwXjbx4",
  authDomain: "financial-chat-6e00a.firebaseapp.com",
  projectId: "financial-chat-6e00a",
  storageBucket: "financial-chat-6e00a.firebasestorage.app",
  messagingSenderId: "872919068959",
  appId: "1:872919068959:web:4b36c8c297fb9c59e9002a",
  measurementId: "G-DF64LP71WN"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { auth, provider, signInWithPopup, signOut };