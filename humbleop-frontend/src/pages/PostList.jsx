// src/pages/PostList.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';

export default function PostList() {
  const { request, loading, error } = useApi();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    async function fetchPosts() {
      const data = await request('/search?q=&type=post&limit=20&sort=desc');
      setPosts(data.posts || []);
    }
    fetchPosts();
  }, [request]);

  if (loading) return <p className="text-center text-white py-8">Loading posts...</p>;
  if (error) return <p className="text-red-400 text-center py-8">{error}</p>;

  return (
    <div className="min-h-screen bg-[#101B13] text-[#E8E5DC] px-4 py-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-[#7FAF92] mb-4">All Posts</h1>

        {posts.length === 0 ? (
          <p className="text-gray-400 italic">No posts found.</p>
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
                  Votes end in: {post.voting_ends_in} sec — Winner: {post.winner || '—'}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
