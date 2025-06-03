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
      const duelCommentsData = await request(`/duel_comments/${id}`);
      const profileData = await request('/profile');

      setPost(postData);
      setComments(Array.isArray(duelCommentsData) ? duelCommentsData : []);
      setCurrentUser(profileData.username);

      if (!postData.started) {
        navigate(`/victory/${id}`);
      }
    } catch (err) {
      console.error("Duel fetch failed:", err);
      toast.error("Failed to load duel data");
    }
  }, [id, token, navigate, request]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) {
      toast.error("Comment cannot be empty.");
      return;
    }
    try {
      await request(`/duel_comment/${id}`, 'POST', { text });
      toast.success("Comment submitted!");
      setText("");
      // Refresh comments after submitting
      const updatedComments = await request(`/duel_comments/${id}`);
      setComments(Array.isArray(updatedComments) ? updatedComments : []);
    } catch (err) {
      console.error("Comment submit failed:", err);
      toast.error("Failed to submit comment");
    }
  }

  if (loading && !post) return <p className="text-center text-white py-8">Loading duel...</p>;
  if (!post) return <p className="text-center text-red-400 py-8">Post not found or not loaded.</p>;

  const duelers = [post.author, post.winner].filter(Boolean);

  // Turno calcolato in base al numero di commenti attuali
  const isUser1Turn = comments.length % 2 === 0;
  const currentTurnUser = isUser1Turn ? duelers[0] : duelers[1];

  const canComment = currentUser === currentTurnUser && duelers.includes(currentUser);

  console.log("post.author =", post.author);
  console.log("post.winner =", post.winner);
  console.log("duelers =", duelers);
  console.log("comments =", comments);
  console.log("currentTurnUser =", currentTurnUser);
  console.log("currentUser =", currentUser);
  console.log("canComment =", canComment);


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
            {duelers.map(user => (
              <li key={user}>{user}</li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="font-semibold mb-2 text-[#5D749B]">Duel Comments</h2>
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
              placeholder="Write your duel comment here..."
              rows={4}
              className="w-full p-2 rounded border text-black"
            />
            <button
              type="submit"
              className="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              disabled={loading}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
        )}

        {!canComment && (
          <p className="text-gray-400 italic mt-4">
            It is {currentTurnUser || "unknown user"}&apos;s turn to comment.
          </p>
        )}
      </div>
    </div>
  );
}
