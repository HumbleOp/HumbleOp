import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';

import logo from '../assets/logo.png';
import registerBg from '../assets/login-bg.png'; // Puoi sostituirlo con un'immagine dedicata

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        toast.error(data.error || 'Registration failed');
        return;
      }
      toast.success('Registration successful! Redirecting to login...');
      setTimeout(() => navigate('/'), 1500);
    } catch (err) {
      toast.error(err.message || 'An error occurred');
    }
  }

  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2">
      {/* Left: Registration Form with gradient */}
      <div
        className="flex flex-col justify-center items-start md:items-center px-8 py-12 space-y-8"
        style={{
          background: 'linear-gradient(to right, #101B13 0%, #172d1a 25%, #112216 80%, #112216 100%)',
          color: 'white',
        }}
      >
        <img src={logo} alt="HumbleOp Logo" className="h-84 md:h-72" />

        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold text-[#E8E5DC] tracking-wide">
            Join HumbleOp
          </h1>
          <p className="text-sm text-gray-400 max-w-sm">
            Dive into engaging debates, earn badges, and show your support or raise flags. Become a part of our community today!
          </p>
        </div>

        <form onSubmit={handleRegister} className="w-full max-w-sm space-y-5">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 rounded bg-[#1A2A20] text-white border border-[#5D749B] focus:outline-none focus:ring-2 focus:ring-[#7FAF92]"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 rounded bg-[#1A2A20] text-white border border-[#5D749B] focus:outline-none focus:ring-2 focus:ring-[#7FAF92]"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 rounded bg-[#1A2A20] text-white border border-[#5D749B] focus:outline-none focus:ring-2 focus:ring-[#7FAF92]"
            required
          />
          <button
            type="submit"
            className="w-full bg-[#7FAF92] text-black py-3 rounded font-semibold tracking-wide hover:bg-[#5D749B] hover:text-white transition"
          >
            REGISTER
          </button>
          <p className="text-sm text-gray-400 text-center">
            Already have an account?{' '}
            <Link to="/" className="text-[#7FAF92] underline">
              Log in here
            </Link>
          </p>
        </form>
      </div>

      {/* Right: Visual Section */}
      <div
        className="hidden md:flex flex-col justify-center items-center p-8"
        style={{
          backgroundImage: `url(${registerBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Sfondo illustrato */}
      </div>
    </div>
  );
}
