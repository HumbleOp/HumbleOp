// src/pages/CompletedPosts.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import PageContainer from '../components/PageContainer';

export default function CompletedPosts() {
  const { request, loading, error } = useApi();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    async function fetchCompleted() {
      const data = await request('/posts?type=completed');
      setPosts(data.posts || []);
    }
    fetchCompleted();
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
                <p className="text-sm text-gray-400 mt-1">by {post.author}</p>
                <p className="text-sm text-[#5D749B] mt-1">
                  Winner: {post.winner || '—'} — Second: {post.second || '—'}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </PageContainer>
  );
}
