// src/pages/CompletedPosts.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../context/AuthContext';
import PageContainer from '../components/PageContainer';

export default function CompletedPosts() {
  const { request, loading, error } = useApi();
  const [posts, setPosts] = useState([]);

  const { token } = useAuth();
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    async function fetchCompleted() {
      const data = await request('/posts?type=completed');
      setPosts(data.posts || []);
    }
    fetchCompleted();
    if (token) {
      fetch("http://localhost:5000/profile", {
        headers: { Authorization: "Bearer " + token }
    })
      .then((res) => res.json())
      .then((data) => setCurrentUser(data.username));
    }

  }, [request]);

  if (loading) return <p className="text-center text-white py-8">Loading completed posts...</p>;
  if (error) return <p className="text-red-400 text-center py-8">{error}</p>;

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-[#7FAF92] mb-4">Completed Posts</h1>

        {posts.length === 0 ? (
          <p className="text-gray-400 italic">No completed posts yet.</p>
        ) : (
          <ul className="space-y-4">
            {posts.map((post) => (
              <li
                key={post.id}
                className="bg-[#1A2A20] p-4 rounded shadow hover:shadow-md transition"
              >
                <Link
                  to={`/post/${post.id}`}
                  className="text-lg font-semibold text-[#E8E5DC] hover:text-[#7FAF92]"
                >
                  {post.body.length > 100 ? post.body.slice(0, 100) + '...' : post.body}
                </Link>
                <p className="text-sm text-gray-400 mt-1">
                  by <Link to={currentUser === post.author ? '/profile' : `/profile/${post.author}`} className="text-[#A1D9B4] hover:underline">{post.author}</Link>
                </p>
                <p className="text-sm text-[#5D749B] mt-1">
                  Winner:{' '}
                  {post.winner ? (
                    <Link to={currentUser === post.winner ? '/profile' : `/profile/${post.winner}`} className="text-[#A1D9B4] hover:underline">
                      {post.winner}
                    </Link>
                  ) : '—'}
                  {' — '}
                  Second:{' '}
                  {post.second ? (
                    <Link to={currentUser === post.second ? '/profile' : `/profile/${post.second}`} className="text-[#A1D9B4] hover:underline">
                      {post.second}
                    </Link>
                  ) : '—'}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </PageContainer>
  );
}
