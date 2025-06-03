import { useState } from 'react';
import logo from '../assets/logo.png';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (!res.ok) {
        toast.error(data.error || 'Login failed');
      } else {
        login(data.access_token);
        toast.success('Login successful!');
        navigate('/posts');
      }
    } catch (err) {
      toast.error(err.message || 'Login error');
    }
  }

  return (
    <div className="min-h-screen bg-[#101B13] text-[#E8E5DC] flex flex-col items-center justify-center p-4">
      {/* LOGO */}
      <img
        src={logo}
        alt="HumbleOp Logo"
        className="w-80 h-80 mb-10"
      />
      <form
        onSubmit={handleLogin}
        className="bg-[#1A2A20] p-8 rounded shadow w-full max-w-md"
      >
        <h1 className="text-2xl font-bold mb-6 text-[#7FAF92]">Welcome</h1>

        <label className="block mb-2">Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-2 mb-4 rounded border text-black"
          required
        />

        <label className="block mb-2">Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 mb-6 rounded border text-black"
          required
        />

        <button
          type="submit"
          className="w-full bg-[#7FAF92] text-black py-2 px-4 rounded hover:bg-[#5D749B]"
        >
          Login
        </button>
      </form>

      {/* REGISTRATION LINK */}
      <p className="mt-4 text-sm text-[#E8E5DC]">
        New to HumbleOp?{' '}
        <Link to="/register" className="text-[#7FAF92] underline hover:text-[#A1D9B4]">
          Sign up here!
        </Link>
      </p>
    </div>
  );
}
