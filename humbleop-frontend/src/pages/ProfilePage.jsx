// src/pages/ProfilePage.jsx
import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import PageContainer from '../components/PageContainer';

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
      toast.success('Bio updated');
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

  if (!profile) return <p className="text-center py-8">Loading profile...</p>;

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto p-6">
        <h2 className="text-2xl font-bold mb-6 text-[#7FAF92]">Welcome, {profile.username}!</h2>

        <div className="grid md:grid-cols-3 gap-6 items-start">
          <div className="col-span-1">
            <strong className="block mb-2 text-[#5D749B]">Avatar:</strong>
            {profile.avatar_url && !editingAvatar ? (
              <>
                <img
                  src={`http://localhost:5000${profile.avatar_url}?t=${Date.now()}`}
                  alt="avatar"
                  className="rounded shadow w-40 h-40 object-cover"
                />
                <button
                  onClick={() => setEditingAvatar(true)}
                  className="mt-2 text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B]"
                >
                  Edit Avatar
                </button>
              </>
            ) : (
              <div className="flex flex-col gap-2">
                <input type="file" ref={fileRef} accept="image/*" />
                <button
                  onClick={uploadAvatar}
                  className="text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B]"
                >
                  Upload Avatar
                </button>
              </div>
            )}
          </div>

          <div className="col-span-2">
            <strong className="block mb-2 text-[#5D749B]">Bio:</strong>
            {editingBio || !profile.bio ? (
              <div className="flex flex-col gap-2">
                <textarea
                  value={bioInput}
                  onChange={e => setBioInput(e.target.value)}
                  rows={4}
                  className="w-full p-2 border rounded text-black"
                />
                <button
                  onClick={updateProfile}
                  className="self-start text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B]"
                >
                  Save Bio
                </button>
              </div>
            ) : (
              <p className="flex justify-between items-center">
                <span>{profile.bio}</span>
                <button
                  onClick={() => setEditingBio(true)}
                  className="text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B]"
                >
                  Edit Bio
                </button>
              </p>
            )}

            <div className="mt-6">
              <strong className="block text-[#5D749B] mb-2">Badges:</strong>
              <div className="flex flex-wrap gap-2">
                {(profile.badges || []).map((badge, i) => (
                  <span
                    key={i}
                    className="text-xs bg-[#E8E5DC] text-[#101B13] px-2 py-1 rounded shadow"
                  >
                    {badge}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-6 flex gap-4 text-sm">
              <Link to="/create" className="text-[#7FAF92] underline">
                📝 New Post
              </Link>
              <Link to="/posts" className="text-[#7FAF92] underline">
                See all posts
              </Link>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}