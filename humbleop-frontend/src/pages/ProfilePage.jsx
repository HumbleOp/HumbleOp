// src/pages/ProfilePage.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  useEffect(() => {
    fetch('http://localhost:5000/profile', {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })
      .then(res => res.json())
      .then(data => setProfile(data));
  }, [token]);

  if (!profile) return <p>Caricamento...</p>;

  return (
    <div>
      <h2>Benvenuto, {profile.username}!</h2>
      <p>Bio: {profile.bio || 'nessuna bio'}</p>
      <p>Badge: {(profile.badges || []).join(', ')}</p>
      <img src={profile.avatar_url} alt="avatar" style={{ maxWidth: '150px' }} />
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
