// src/pages/ProfilePage.jsx
import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast} from 'react-hot-toast';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [bioInput, setBioInput] = useState('');
  const [editingBio, setEditingBio] = useState(false);
  const [editingAvatar, setEditingAvatar] = useState(false);
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
      toast.success('Bio updated')
      setProfile(data.profile);
      setEditingBio(false);
    } catch (err) {
      toast.error(err.message || 'Update failed.');
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
      toast.success('Avatar updated.');
      setProfile(prev => ({ ...prev, avatar_url: data.avatar_url }));
      setEditingAvatar(false);
    } catch (err) {
      toast.error(err.message || 'Upload failed.');
    }
  }

  if (!profile) return <p>Loading profile...</p>;

  return (
    <div>
      <h2>Welcome, {profile.username}!</h2>

      <div style={{ marginBottom: '1em' }}>
        <strong>Bio:</strong><br />
        {editingBio || !profile.bio ? (
          <div>
            <textarea
              value={bioInput}
              onChange={e => setBioInput(e.target.value)}
              rows={3}
              style={{ width: '100%' }}
            />
            <button onClick={updateProfile}>Save Bio</button>
          </div>
        ) : (
          <p>
            {profile.bio} <button onClick={() => setEditingBio(true)}>Edit Bio</button>
          </p>
        )}
      </div>

      <div style={{ marginBottom: '1em' }}>
        <strong>Avatar:</strong><br />
        {profile.avatar_url && !editingAvatar ? (
          <>
            <img
              src={`http://localhost:5000${profile.avatar_url}?t=${Date.now()}`}
              alt="avatar"
              style={{ maxWidth: '150px' }}
            /><br />
            <button onClick={() => setEditingAvatar(true)}>Edit Avatar</button>
          </>
        ) : (
          <div>
            <input type="file" ref={fileRef} accept="image/*" />
            <button onClick={uploadAvatar}>Upload Avatar</button>
          </div>
        )}
      </div>

      <p>Badges: {(profile.badges || []).join(', ')}</p>
      <p><Link to="/create">📝 New Post</Link></p>
      <p><Link to="/posts">See all posts</Link></p>
    </div>
  );
}
