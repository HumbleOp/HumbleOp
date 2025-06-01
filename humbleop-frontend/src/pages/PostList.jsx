// src/pages/PostList.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';


export default function PostList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchPosts() {
      try {
        const res = await fetch('http://localhost:5000/search?q=&type=post&limit=20&sort=desc');
        const data = await res.json();
        if (res.ok) {
          setPosts(data.posts);
        } else {
          setError(data.error || 'Failed to fetch posts');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchPosts();
  }, []);

  if (loading) return <p>Loading posts...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2>Latest Posts</h2>
      {posts.length === 0 ? (
        <p>No posts found.</p>
      ) : (
        posts.map(post => (
          <div key={post.id} style={{ border: '1px solid #ccc', padding: '1em', marginBottom: '1em' }}>
            <p><strong>Author:</strong> {post.author}</p>
            <p>
              <Link to={`/post/${post.id}`} className="text-blue-600 hover:underline">
                {post.body}
              </Link>
            </p>
            {post.winner && (
              <p className="text-sm text-green-700 mt-1">
                🏆 <Link to={`/victory/${post.id}`} className="underline text-green-700 hover:text-green-900">
                  View duel summary
                </Link>
                {post.second && (
                  <>
                    {" | "}
                    <Link to={`/duel/${post.id}`} className="underline text-yellow-600 hover:text-yellow-800">
                      👉 Go to duel
                    </Link>
                  </>
                )}
              </p>
            )}
          </div>
        ))
      )}
    </div>
  );
}