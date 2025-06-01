// src/pages/DuelPage.jsx
import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useApi } from '../hooks/useApi';
import { toast } from "react-hot-toast";

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
      // error handled by useApi
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
      // error handled by useApi
    }
  }

  if (loading && !post) return <p className="text-center text-white py-8">Loading duel...</p>;

  const duelers = [post?.winner, post?.second];
  const canComment = duelers.includes(currentUser);

  return (
    <div className="min-h-screen bg-[#101B13] text-[#E8E5DC] px-4 py-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-xl font-bold mb-2 text-[#7FAF92]">Duel in Progress</h1>

        {error && <p className="text-red-400 mb-2">{error}</p>}

        <div className="bg-[#1A2A20] shadow rounded-xl p-4 mb-4">
          <p className="text-sm text-gray-400">
            Posted by <strong className="text-[#E8E5DC]">{post.author}</strong>
          </p>
          <p className="mt-2 text-lg text-[#E8E5DC]">{post.body}</p>
        </div>

        <div className="bg-[#1F2F25] border border-[#5D749B] rounded-xl p-4 mb-4">
          <p className="text-sm text-[#7FAF92] font-semibold mb-1">Duel Participants:</p>
          <ul className="list-disc list-inside text-sm">
            <li>{post.winner}</li>
            <li>{post.second}</li>
          </ul>
        </div>

        <div>
          <h2 className="font-semibold mb-2 text-[#5D749B]">Comments</h2>
          {comments.length === 0 ? (
            <p className="italic text-gray-400">No comments yet.</p>
          ) : (
            <ul className="space-y-2">
              {comments.map((c, i) => (
                <li key={i} className="bg-[#142017] p-3 rounded shadow">
                  <strong>{c.commenter}</strong>: {c.text}
                </li>
              ))}
            </ul>
          )}
        </div>

        {canComment && (
          <form onSubmit={handleSubmit} className="mt-6">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Your duel comment..."
              rows={4}
              className="w-full p-2 border rounded text-black"
            ></textarea>
            <button
              type="submit"
              className="mt-2 bg-[#7FAF92] text-black px-4 py-2 rounded hover:bg-[#5D749B]"
              disabled={loading}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
        )}

        {!canComment && (
          <p className="text-gray-400 italic mt-4">
            Only duel participants can comment.
          </p>
        )}
      </div>
    </div>
  );
}
