// src/pages/ProfilePage.jsx
import { useEffect, useState } from 'react';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/profile', {
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      }
    })
      .then(res => res.json())
      .then(data => setProfile(data));
  }, []);

  if (!profile) return <p>Caricamento...</p>;

  return (
    <div>
      <h2>Benvenuto, {profile.username}!</h2>
      <p>Bio: {profile.bio || 'nessuna bio'}</p>
      <p>Badge: {profile.badges.join(', ')}</p>
      <img src={profile.avatar_url} alt="avatar" style={{ maxWidth: '150px' }} />
    </div>
  );
}
