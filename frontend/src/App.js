import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Configurar URL del API - cambia esto cuando subas el backend
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [currentPage, setCurrentPage] = useState('login');
  const [imageFile, setImageFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchUserData();
    }
  }, [token]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data.user);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    const formData = new FormData(e.target);
    
    try {
      await axios.post(`${API_URL}/auth/register`, {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password')
      });
      setCurrentPage('login');
    } catch (error) {
      setError(error.response?.data?.error || 'Error en el registro');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    const formData = new FormData(e.target);
    
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        username: formData.get('username'),
        password: formData.get('password')
      });
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
      setUser(response.data.user);
      setCurrentPage('analyze');
    } catch (error) {
      setError(error.response?.data?.error || 'Error en el login');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/auth/logout`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Error en logout:', error);
    }
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setCurrentPage('login');
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setAnalysisResult(null);
      setError('');
    }
  };

  const handleAnalyze = async () => {
    if (!imageFile) {
      setError('Por favor selecciona una imagen');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', imageFile);

    try {
      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      setAnalysisResult(response.data);
    } catch (error) {
      setError(error.response?.data?.error || 'Error al analizar la imagen');
    } finally {
      setLoading(false);
    }
  };

  if (!token || !user) {
    return (
      <div className="container">
        <div className="auth-box">
          <h1>🔒 Nice Checker</h1>
          <p>Analiza la privacidad de tus fotos antes de subirlas a redes sociales</p>
          
          {error && <div className="error">{error}</div>}
          
          {currentPage === 'login' ? (
            <form onSubmit={handleLogin} className="auth-form">
              <h2>Iniciar Sesión</h2>
              <input name="username" placeholder="Usuario" required />
              <input name="password" type="password" placeholder="Contraseña" required />
              <button type="submit">Entrar</button>
              <p>
                ¿No tienes cuenta? <button type="button" onClick={() => setCurrentPage('register')}>Regístrate</button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="auth-form">
              <h2>Registrarse</h2>
              <input name="username" placeholder="Usuario" required />
              <input name="email" type="email" placeholder="Email" required />
              <input name="password" type="password" placeholder="Contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)" required />
              <button type="submit">Registrarse</button>
              <p>
                ¿Ya tienes cuenta? <button type="button" onClick={() => setCurrentPage('login')}>Inicia sesión</button>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🔒 NiceChecker</h1>
        <div className="user-info">
          <span>👤 {user.username}</span>
          <button onClick={handleLogout}>Cerrar Sesión</button>
        </div>
      </div>

      <div className="main-content">
        <div className="welcome-message">
          🎉 ¡Bienvenido a NiceChecker! Sube tu foto y nuestra IA te dirá si es seguro compartirla en redes sociales.
        </div>
        <div className="upload-section">
          <h2>📸 Sube tu foto para analizar</h2>
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleImageUpload}
            className="file-input"
          />
          {imageFile && (
            <div className="preview">
              <img src={URL.createObjectURL(imageFile)} alt="Preview" />
              <p>{imageFile.name}</p>
            </div>
          )}
          <button 
            onClick={handleAnalyze} 
            disabled={loading || !imageFile}
            className="analyze-button"
          >
            {loading ? 'Analizando...' : '🔍 Analizar Foto'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {analysisResult && (
          <div className="results">
            <h2>📊 Resultados del Análisis</h2>
            
            <div className="result-section">
              <h3>📍 Exposición de Ubicación</h3>
              <div className={`level ${analysisResult.location_exposure}`}>
                <strong>Nivel: {analysisResult.location_exposure.toUpperCase()}</strong>
              </div>
              {analysisResult.has_gps && (
                <p>⚠️ Coordenadas GPS: {analysisResult.gps_coordinates}</p>
              )}
              {analysisResult.location_details && analysisResult.location_details.length > 0 && (
                <ul>
                  {analysisResult.location_details.map((detail, idx) => (
                    <li key={idx}>{detail}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="result-section">
              <h3>👤 Exposición Corporal</h3>
              <div className={`level ${analysisResult.body_exposure}`}>
                <strong>Nivel: {analysisResult.body_exposure.replace('_', ' ').toUpperCase()}</strong>
              </div>
              {analysisResult.has_faces && (
                <p>👥 Rostros detectados: {analysisResult.face_count}</p>
              )}
              {analysisResult.exposure_details && analysisResult.exposure_details.length > 0 && (
                <ul>
                  {analysisResult.exposure_details.map((detail, idx) => (
                    <li key={idx}>{detail}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="result-section recommendations">
              <h3>💡 Recomendaciones</h3>
              <ul>
                {analysisResult.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
