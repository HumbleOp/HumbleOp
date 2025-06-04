// src/pages/PublicProfilePage.jsx
import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function PublicProfilePage() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);

    useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`http://localhost:5000/user/${username}`, {
        headers: {
        Authorization: "Bearer " + token
        }
    })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
        if (ok) setProfile(data);
        else setProfile(null);
        })
        .catch(() => setProfile(null));
    }, [username]);

  if (!profile) return <p className="text-center text-white py-8">Loading user...</p>;

  return (
    <div className="max-w-2xl mx-auto py-6 text-[#E8E5DC]">
      <h1 className="text-2xl font-bold text-[#7FAF92] mb-2">@{username}</h1>
      <p className="text-gray-300 mb-2">{profile.bio || 'No bio provided.'}</p>

      <div className="text-sm text-gray-400 space-y-1">
        <p>Followers: {profile.followers?.length || 0}</p>
        <p>Following: {profile.following?.length || 0}</p>
        <p>Badges: {(profile.badges || []).join(', ') || '—'}</p>
      </div>
    </div>
  );
}
