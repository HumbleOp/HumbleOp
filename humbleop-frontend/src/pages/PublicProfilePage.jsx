// src/pages/PublicProfilePage.jsx
import { useParams, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import PageContainer from '../components/PageContainer';

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

  if (!profile) return <p className="text-center py-8 text-white">Loading user...</p>;
  if (error) return <p className="text-center py-8 text-red-400">{error}</p>;

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto p-6">
        <h2 className="text-2xl font-bold mb-6 text-[#7FAF92]">@{username}</h2>

        <div className="grid md:grid-cols-3 gap-6 items-start">
          <div className="col-span-1">
            {profile.avatar_url && (
              <img
                src={`http://localhost:5000${profile.avatar_url}`}
                alt={`${username}'s avatar`}
                className="rounded shadow w-40 h-40 object-cover"
              />
            )}
          </div>

          <div className="col-span-2">
          <strong className="block mb-2 text-[#5D749B]">Bio:</strong>
          <p className="mb-4 text-[#E8E5DC]">
            {profile.bio ||
              "No bio provided."
            }
          </p>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
              <div>
                <h3 className="text-[#7FAF92] font-semibold mb-2">Followers</h3>
                {profile.followers?.length > 0 ? (
                  <ul className="space-y-1">
                    {profile.followers.map((u) => (
                      <li key={u}>
                        <Link
                          to={u === currentUser ? "/profile" : `/profile/${u}`}
                          className="text-[#A1D9B4] hover:underline"
                        >
                          {u}
                        </Link>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="italic text-gray-500">No followers yet.</p>
                )}
              </div>

              <div>
                <h3 className="text-[#7FAF92] font-semibold mb-2">Following</h3>
                {profile.following?.length > 0 ? (
                  <ul className="space-y-1">
                    {profile.following.map((u) => (
                      <li key={u}>
                        <Link
                          to={u === currentUser ? "/profile" : `/profile/${u}`}
                          className="text-[#A1D9B4] hover:underline"
                        >
                          {u}
                        </Link>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="italic text-gray-500">Not following anyone.</p>
                )}
              </div>
            </div>

            <div className="mt-6">
            <strong className="block text-[#5D749B] mb-2">Badges:</strong>
            <div className="flex flex-wrap gap-2">
              {(profile.badges || []).map((badge, i) => (
                <img
                  key={i}
                  src={require(`../assets/badges/${badge.toLowerCase().replace(/ /g, '_')}.png`)}
                  alt={badge}
                  className="w-12 h-12"
                />
              ))}
            </div>
            </div>

            {currentUser && currentUser !== profile.username && (
              profile.followers?.includes(currentUser) ? (
                <button
                  onClick={handleUnfollow}
                  className="mt-6 bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                >
                  Unfollow
                </button>
              ) : (
                <button
                  onClick={handleFollow}
                  className="mt-6 bg-[#7FAF92] text-[#E8E5DC] px-3 py-1 rounded hover:bg-[#5D749B]"
                >
                  Follow
                </button>
              )
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
