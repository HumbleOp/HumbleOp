// src/pages/ProfilePage.jsx
import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [bioInput, setBioInput] = useState('');
  const [message, setMessage] = useState('');
  const fileRef = useRef(null);
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
          logout();
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

  // Aggiorna la bio quando arriva il profilo
  useEffect(() => {
    if (profile?.bio !== undefined) {
      setBioInput(profile.bio);
    }
  }, [profile]);

  async function updateProfile() {
    try {
      const res = await fetch('http://localhost:5000/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + token
        },
        body: JSON.stringify({ bio: bioInput })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Update failed');
      setMessage('Profile updated.');
      setProfile(data.profile);
    } catch (err) {
      setMessage(err.message || 'Update failed.');
    }
  }

  async function uploadAvatar() {
    const file = fileRef.current?.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('avatar', file);

    try {
      const res = await fetch('http://localhost:5000/upload_avatar', {
        method: 'POST',
        headers: {
          Authorization: 'Bearer ' + token
        },
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Upload failed');
      setMessage('Avatar updated.');
      setProfile(prev => ({ ...prev, avatar_url: data.avatar_url }));
    } catch (err) {
      setMessage(err.message || 'Upload failed.');
    }
  }

  if (!profile) return <p>Loading profile...</p>;

  return (
    <div>
      <h2>Welcome, {profile.username}!</h2>
      <p>Bio: {profile.bio || 'No bio provided'}</p>
      <p>Badges: {(profile.badges || []).join(', ')}</p>
      <img
        src={profile.avatar_url ? `http://localhost:5000${profile.avatar_url}` : '/default-avatar.png'}
        alt="avatar"
        style={{ maxWidth: '150px' }}
      />

      <div style={{ marginTop: '1em' }}>
        <label>Update Bio:</label>
        <textarea
          value={bioInput}
          onChange={e => setBioInput(e.target.value)}
          rows={3}
          style={{ width: '100%' }}
        />
        <button onClick={updateProfile}>Save Bio</button>
      </div>

      <div style={{ marginTop: '1em' }}>
        <label>Change Avatar:</label>
        <input type="file" ref={fileRef} accept="image/*" />
        <button onClick={uploadAvatar}>Upload Avatar</button>
      </div>

      {message && <p style={{ color: 'green' }}>{message}</p>}

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
