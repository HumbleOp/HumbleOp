// src/pages/RegisterPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

export default function RegisterPage() {
  const [form, setForm] = useState({ username: '', password: '', email: '' });
  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();

    try {
      const res = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();

      if (res.ok) {
        toast.success('Registration successful! Redirecting...');
        setTimeout(() => navigate('/'), 1500);
        return;
      } else {
        toast.error(data.error || 'Registration failed');
      }
    } catch (err) {
      toast.error(err.message || 'Registration failed');
    }
  }

  return (
    <form onSubmit={handleRegister}>
      <h2>Sign up</h2>
      <input
        placeholder="Username"
        value={form.username}
        onChange={e => setForm({ ...form, username: e.target.value })}
      />
      <input
        placeholder="Email"
        value={form.email}
        onChange={e => setForm({ ...form, email: e.target.value })}
      />
      <input
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={e => setForm({ ...form, password: e.target.value })}
      />
      <button type="submit">Register</button>
    </form>
  );
}
