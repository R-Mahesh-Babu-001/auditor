import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { Provider } from "react-redux";
import store from "./redux/store/store.js";
import App from './App.jsx'

/**
 * Application Entry Point
 * 
 * This is the main entry point for the React application.
 * It renders the root App component into the DOM element with id 'root'.
 * 
 * Key responsibilities:
 * - Mounts the React application.
 * - Wraps the App in the Redux Provider to make the store available to all components.
 * - Imports global styles (index.css).
 */
createRoot(document.getElementById('root')).render(
  // <StrictMode> is currently commented out. 
  // Uncommenting it enables additional checks and warnings during development.
  <Provider store={store}>
    <App />
  </Provider>
  // </StrictMode>,
)
