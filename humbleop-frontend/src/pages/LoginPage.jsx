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
      <div className="max-w-4xl mx-auto p-6 rounded-lg">
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
                  className="mt-2 text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B] transition"
                >
                  Edit Avatar
                </button>
              </>
            ) : (
              <div className="flex flex-col gap-2">
                <input type="file" ref={fileRef} accept="image/*" className="text-sm text-gray-400" />
                <button
                  onClick={uploadAvatar}
                  className="text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B] transition"
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
                  className="w-full p-2 border rounded bg-[#16221C] text-[#E8E5DC]"
                />
                <button
                  onClick={updateProfile}
                  className="self-start text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B] transition"
                >
                  Save Bio
                </button>
              </div>
            ) : (
              <p className="flex justify-between items-center">
                <span className="text-[#E8E5DC]">{profile.bio}</span>
                <button
                  onClick={() => setEditingBio(true)}
                  className="text-sm text-white bg-[#7FAF92] px-3 py-1 rounded hover:bg-[#5D749B] transition"
                >
                  Edit Bio
                </button>
              </p>
            )}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
            <div>
              <h3 className="text-[#7FAF92] font-semibold mb-2">Followers</h3>
              {profile.followers?.length > 0 ? (
                <ul className="space-y-1">
                  {profile.followers.map((u) => (
                    <li key={u}>
                      <Link
                        to={u === profile.username ? "/profile" : `/profile/${u}`}
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
                        to={u === profile.username ? "/profile" : `/profile/${u}`}
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
                    src={`/assets/badges/${badge.toLowerCase()}.png`} // path to badge image
                    alt={badge}
                    className="w-10 h-10"
                  />
                ))}
              </div>
            </div>

            <div className="mt-6 flex gap-4 text-sm">
              <Link to="/create" className="bg-[#7FAF92] text-black px-4 py-2 rounded hover:bg[#5D749B] transition flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                New Post
              </Link>
              <Link to="/posts" className="text-[#7FAF92] underline hover:text-[#A1D9B4]">
                See all posts
              </Link>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
