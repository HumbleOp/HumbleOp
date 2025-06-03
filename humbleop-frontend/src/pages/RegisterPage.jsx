// src/pages/RegisterPage.jsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import logo from '../assets/logo.png';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      const data = await res.json();
      if (!res.ok) {
        toast.error(data.error || 'Registration failed');
      } else {
        toast.success('Registration successful! Redirecting...');
        setTimeout(() => navigate('/'), 1500);
      }
    } catch (err) {
      toast.error(err.message || 'Registration error');
    }
  }

  return (
    <div className="min-h-screen bg-[#101B13] text-[#E8E5DC] flex flex-col items-center justify-center p-4">
      {/* Logo centrato */}
      <img
        src={logo}
        alt="HumbleOp Logo"
        className="w-80 h-80 mb-10"
      />

      <form
        onSubmit={handleRegister}
        className="bg-[#1A2A20] p-8 rounded shadow w-full max-w-md"
      >
        <h1 className="text-2xl font-bold mb-6 text-[#7FAF92]">Create your account</h1>

        <label className="block mb-2">Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-2 mb-4 rounded border text-black"
          required
        />

        <label className="block mb-2">Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          Register
        </button>
      </form>

      {/* Link login sotto il form */}
      <p className="mt-4 text-sm text-[#E8E5DC]">
        Already have an account?{' '}
        <Link to="/" className="text-[#7FAF92] underline hover:text-[#A1D9B4]">
          Log in
        </Link>
      </p>
    </div>
  );
}
