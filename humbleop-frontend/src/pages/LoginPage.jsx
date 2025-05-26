// src/LoginPage.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(e) {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok) {
        login(data.token);     // usa il context
        navigate('/profile');  // reindirizza
      } else {
        setError(data.error || 'Errore');
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <form onSubmit={handleLogin}>
        <div>
          <input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </div>
        <button type="submit">Login</button>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </form>

      <p>
        New to HumbleOp? <Link to="/register">Registrati</Link>
      </p>
    </>
  );
}
