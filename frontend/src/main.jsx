// Application entry point. Mounts the React app into the <div id="root"> element
// in index.html. StrictMode is enabled so React flags unsafe patterns during
// development; it renders nothing itself and has no effect in the production build.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
