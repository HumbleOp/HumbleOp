import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

import logo from '../assets/logo.png';
import loginBg from '../assets/login-bg.png'; // assuming this is the generated illustration

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
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2">
      {/* Left: Login Form with gradient */}
      <div
        className="flex flex-col justify-center items-start md:items-center px-8 py-12 space-y-8"
        style={{
          background: 'linear-gradient(to right, #101B13 0%, #172d1a 25%, #112216 80%, #112216 100%)',
          color: 'white',
        }}
      >
        <img src={logo} alt="HumbleOp Logo" className="h-80 md:h-72" />
        <h1 className="text-3xl md:text-4xl font-bold text-[#E8E5DC] tracking-wide">Log in</h1>
        <form onSubmit={handleLogin} className="w-full max-w-sm space-y-5">
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
            className="w-full bg-[#7FAF92] text-black py-3 rounded font-semibold tracking-wide hover:bg-[#5D749B] hover:text-white transition"
          >
            LOG IN
          </button>
          <p className="text-sm text-gray-400 text-center">
            Don&rsquo;t have an account yet?{' '}
            <Link to="/register" className="text-[#7FAF92] underline">
              Sign up here
            </Link>
          </p>
        </form>
      </div>

      {/* Right: Visual Section */}
      <div
        className="hidden md:flex flex-col justify-center items-center p-8"
        style={{
          backgroundImage: `url(${loginBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Background illustration only */}
      </div>
    </div>
  );
}
