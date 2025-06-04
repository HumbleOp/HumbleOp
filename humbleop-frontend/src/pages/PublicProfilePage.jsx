// src/pages/PublicProfilePage.jsx
import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function PublicProfilePage() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [error, setError] = useState(null);

    useEffect(() => {
    const token = localStorage.getItem("token");

    async function fetchData() {
        try {
        const [profileRes, selfRes] = await Promise.all([
            fetch(`http://localhost:5000/user/${username}`, {
            headers: { Authorization: "Bearer " + token }
            }),
            fetch(`http://localhost:5000/profile`, {
            headers: { Authorization: "Bearer " + token }
            })
        ]);

        const profileData = await profileRes.json();
        const selfData = await selfRes.json();

        if (!profileRes.ok || !selfRes.ok) {
            setError(profileData.error || "Error loading profile.");
            return;
        }

        setProfile(profileData);
        setCurrentUser(selfData.username);
        } catch {
        setError("Failed to fetch profile.");
        }
    }

    if (token) fetchData();
    }, [username]);

    async function handleFollow() {
  const token = localStorage.getItem("token");
  await fetch(`http://localhost:5000/follow/${username}`, {
    method: "POST",
    headers: { Authorization: "Bearer " + token }
  });
  setProfile(prev => ({
    ...prev,
    followers: [...prev.followers, currentUser]
  }));
}

async function handleUnfollow() {
  const token = localStorage.getItem("token");
  await fetch(`http://localhost:5000/unfollow/${username}`, {
    method: "POST",
    headers: { Authorization: "Bearer " + token }
  });
  setProfile(prev => ({
    ...prev,
    followers: prev.followers.filter(u => u !== currentUser)
  }));
}


  if (!profile) return <p className="text-center text-white py-8">Loading user...</p>;

  return (
    <div className="max-w-2xl mx-auto py-6 text-[#E8E5DC]">
      <h1 className="text-2xl font-bold text-[#7FAF92] mb-2">@{username}</h1>
      <p className="text-gray-300 mb-2">{profile.bio || 'No bio provided.'}</p>

      <div className="text-sm text-gray-400 space-y-1">
        <p>Followers: {profile.followers?.length || 0}</p>
        <p>Following: {profile.following?.length || 0}</p>
        <p>Badges: {(profile.badges || []).join(', ') || '—'}</p>
        {currentUser && currentUser !== profile.username && (
        profile.followers?.includes(currentUser) ? (
            <button
            onClick={handleUnfollow}
            className="mt-4 bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
            >
            Unfollow
            </button>
        ) : (
            <button
            onClick={handleFollow}
            className="mt-4 bg-[#7FAF92] text-black px-3 py-1 rounded hover:bg-[#5D749B]"
            >
            Follow
            </button>
        )
        )}
      </div>
    </div>
  );
}
