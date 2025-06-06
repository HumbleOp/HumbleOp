// src/pages/LoginPage.jsx

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

import logo from '../assets/logo.png';
// Importa qui il tuo sfondo personalizzato
import customBg from '../assets/bg_log_reg.png';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    const res = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      toast.error(data.error || 'Login failed');
      return;
    }
    login(data.access_token);
    navigate('/posts');
  }

  return (
    <div
      className="min-h-screen flex flex-col md:flex-row"
      style={{
        backgroundImage: `url(${customBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="flex-1 flex justify-center items-center px-8 py-12">
        <div className="w-full max-w-md space-y-8 bg-black/50 p-6 rounded">
         <h1 className="text-3xl font-bold text-[#E8E5DC] text-center">Log in</h1>
          <form onSubmit={handleLogin} className="space-y-5">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 rounded bg-[#1A2A20] text-white border border-[#5D749B] focus:outline-none focus:ring-2 focus:ring-[#7FAF92]"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded bg-[#1A2A20] text-white border border-[#5D749B] focus:outline-none focus:ring-2 focus:ring-[#7FAF92]"
            />
            <button
              type="submit"
              className="w-full bg-[#7FAF92] text-[#E8E5DC] py-3 rounded font-semibold tracking-wide hover:bg-[#5D749B] hover:text-white transition"
            >
              LOG IN
            </button>
            <p className="text-sm text-gray-200 text-center">
              Don&apos;t have an account yet?{' '}
              <Link to="/register" className="text-[#7FAF92] underline">
                Register here
              </Link>
            </p>
          </form>
        </div>
      </div>
      {/* Se non serve una seconda colonna, puoi toglierla */}
    </div>
  );
}
