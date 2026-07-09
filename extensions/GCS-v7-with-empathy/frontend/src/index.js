import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // A file for global styles
import App from './App';

// 1. Find the 'root' div in your public/index.html file.
const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);

// 2. Tell React to render our main App component inside of it.
// <React.StrictMode> is a helper that checks for potential problems in the app.
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
