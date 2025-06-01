// src/LoginPage.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(e) {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      console.log('Login response:', data);
      if (res.ok) {
        login(data.access_token);
        toast.success('Login successful!');
        navigate('/profile');
      } else {
        toast.error(data.error || 'Login failed');
      }
    } catch (err) {
      toast.error(err.message || 'Login error');
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
      </form>

      <p>
        New to HumbleOp? <Link to="/register">Sign up</Link>
      </p>
    </>
  );
}
