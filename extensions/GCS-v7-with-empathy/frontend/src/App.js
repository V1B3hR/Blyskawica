import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere, Text } from '@react-three/drei';
import './App.css';

const BrainModel = ({ activityDots }) => {
  return (
    <>
      <Text position={[0, 2.5, 0]} fontSize={0.3} color="white">
        3D Neural Activity
      </Text>
      <Sphere args={[2, 32, 32]}>
        <meshStandardMaterial color="#333" wireframe />
      </Sphere>
    </>
  );
};

function App() {
  const [systemStatus, setSystemStatus] = useState({ text: 'CONNECTING...', color: 'orange' });
  const [affectiveState, setAffectiveState] = useState(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');

      ws.onopen = () => setSystemStatus({ text: 'CONNECTED', color: 'green' });
      ws.onmessage = (event) => setAffectiveState(JSON.parse(event.data).affective);
      ws.onclose = () => {
        setSystemStatus({ text: 'DISCONNECTED', color: 'red' });
        setTimeout(connectWebSocket, 3000); // Attempt to reconnect after 3 seconds
      };
      ws.onerror = () => ws.close();
    };
    connectWebSocket();
  }, []);

  const getStrengthColor = (strength) => {
    if (strength >= 40 && strength <= 60) return 'green';
    if (strength > 60 && strength <= 80) return 'orange';
    return 'red';
  };

  return (
    <div className="App">
      <header className="header-bar">
        <div className="header-title">Grand Council Sentient</div>
        <div className={`status-indicator ${systemStatus.color}`}>{systemStatus.text}</div>
        <div className="user-profile">V1B3hr</div>
      </header>

      <main className="main-content">
        <div className="left-column">
          <div className="column-title">Physiological & Neural State</div>
          <div className="canvas-container">
            <Canvas>
              <ambientLight intensity={0.8} />
              <pointLight position={[10, 10, 10]} />
              <BrainModel />
              <OrbitControls />
            </Canvas>
          </div>
        </div>

        <div className="right-column">
          <div className="column-title">Affective (Emotional) State</div>
          <div className="emotion-display">
            {affectiveState ? (
              <>
                <div className="emotion-icon">{affectiveState.icon}</div>
                <div className="emotion-label">{affectiveState.label}</div>
                <div className="emotion-strength">
                  <div className="strength-bar-container">
                    <div className={`strength-bar ${getStrengthColor(affectiveState.strength)}`} style={{ width: `${affectiveState.strength}%` }}></div>
                  </div>
                  <span className="strength-percent">{affectiveState.strength}%</span>
                </div>
                <div className={`safe-zone-indicator ${getStrengthColor(affectiveState.strength)}`}>
                  {affectiveState.strength >= 40 && affectiveState.strength <= 60 ? 'Homeostatic Range' : 'Outside Range'}
                </div>
              </>
            ) : (
              <div className="loading-state">Awaiting data...</div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
