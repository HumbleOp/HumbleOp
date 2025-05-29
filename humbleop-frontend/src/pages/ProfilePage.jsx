// src/pages/ProfilePage.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate();
  const { token, logout } = useAuth();

useEffect(() => {
  async function fetchProfile() {
    try {
      const res = await fetch('http://localhost:5000/profile', {
        headers: { Authorization: 'Bearer ' + token }
      });
      const data = await res.json();
      if (!res.ok) {
        logout(); // rimuove token se è invalido
        navigate('/');
      } else {
        setProfile(data);
      }
    } catch {
      logout();
      navigate('/');
    }
  }

  if (token) {
    fetchProfile();
  }
}, [token, logout, navigate]);

if (!profile) return <p>Loading profile...</p>;

  return (
    <div>
      <h2>Welcome, {profile.username}!</h2>
      <p>Bio: {profile.bio || 'No bio provided'}</p>
      <p>Badges: {(profile.badges || []).join(', ')}</p>
      <img src={profile.avatar_url} alt="avatar" style={{ maxWidth: '150px' }} />
      <p>
        <Link to="/create">📝 New Post</Link>
      </p>
      <p>
        <Link to="/posts">See all posts</Link>
      </p>
      <div style={{ marginTop: '1em' }}>
        <button onClick={() => {
          logout();
          navigate('/');
        }}>
          Logout
        </button>
      </div>
    </div>
  );
}
