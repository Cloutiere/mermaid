// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom' // Importation de BrowserRouter
import App from './App' 
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Enveloppement du composant App dans BrowserRouter pour activer le routage */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)