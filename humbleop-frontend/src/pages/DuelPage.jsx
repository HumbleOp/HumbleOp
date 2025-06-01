import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useApi } from '../hooks/useApi';
import { toast } from 'react-hot-toast';

export default function DuelPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const { request, loading, error } = useApi();

  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [text, setText] = useState("");
  const [currentUser, setCurrentUser] = useState(null);

  const fetchData = useCallback(async () => {
    if (!token) return;

    try {
      const postData = await request(`/status/${id}`);
      const commentData = await request(`/comments/${id}`);
      const profileData = await request('/profile');

      setPost(postData);
      setComments(commentData.comments || []);
      setCurrentUser(profileData.username);

      if (!postData.started) {
        navigate(`/victory/${id}`);
      }
    } catch {
      // error already managed by useApi
    }
  }, [id, token, navigate, request]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await request(`/comment/${id}`, 'POST', { text });
      toast.success("Comment submitted!");
      setText("");
      setComments([...comments, { commenter: currentUser, text, votes: 0 }]);
    } catch {
      // error already managed by useApi
    }
  }

  if (loading && !post) return <p>Loading duel...</p>;

  const duelers = [post?.winner, post?.second];
  const canComment = duelers.includes(currentUser);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-2">Duel in Progress</h1>

      {error && <p className="text-red-600 mb-2">{error}</p>}

      <div className="bg-white shadow rounded-xl p-4 mb-4">
        <p className="text-sm text-gray-500">
          Posted by <strong>{post.author}</strong>
        </p>
        <p className="mt-2 text-lg">{post.body}</p>
        {post.winner && post.second && (
          <p className="mt-1 text-sm text-blue-600 font-semibold">
            👉 <a href={`/duel/${post.id}`} className="underline">Go to duel</a>
          </p>
        )}
      </div>

      <div className="bg-yellow-50 border border-yellow-300 rounded-xl p-4 mb-4">
        <p className="text-sm text-gray-700 font-semibold mb-1">Duel Participants:</p>
        <ul className="list-disc list-inside text-sm">
          <li>{post.winner}</li>
          <li>{post.second}</li>
        </ul>
      </div>

      <div>
        <h2 className="font-semibold mb-2">Comments</h2>
        {comments.length === 0 ? (
          <p>No comments yet.</p>
        ) : (
          <ul className="space-y-2">
            {comments.map((c, i) => (
              <li key={i} className="bg-gray-50 p-3 rounded shadow">
                <strong>{c.commenter}</strong>: {c.text}
              </li>
            ))}
          </ul>
        )}
      </div>

      {canComment && (
        <form onSubmit={handleSubmit} className="mt-4">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Your duel comment..."
            rows={4}
            className="w-full p-2 border rounded"
          ></textarea>
          <button type="submit" className="mt-2 bg-blue-600 text-white px-4 py-2 rounded" disabled={loading}>
            {loading ? 'Sending...' : 'Send'}
          </button>          
        </form>
      )}

      {!canComment && (
        <p className="text-gray-500 italic mt-4">
          Only duel participants can comment.
        </p>
      )}
    </div>
  );
}
