import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useApi } from '../hooks/useApi';
import { toast } from "react-hot-toast";
import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer";

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
    } catch (err) {
      console.error("Duel fetch failed:", err);
      toast.error("Failed to load duel data");
    }
  }, [id, token, request]);

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
      const updatedComments = await request(`/duel_comments/${id}`);
      setComments(Array.isArray(updatedComments) ? updatedComments : []);
    } catch (err) {
      console.error("Comment submit failed:", err);
      toast.error("Failed to submit comment");
    }
  }

  async function handleCompleteDuel() {
  try {
    await request(`/complete_duel/${post.id}`, 'POST');
    toast.success("You proposed to end the duel.");
    fetchData();
  } catch (err) {
    toast.error(err.message || "Failed to send completion request.");
  }
}


  if (loading && !post) return <p className="text-center text-white py-8">Loading duel...</p>;
  if (!post || !post.winner || !post.author) return <p className="text-center text-white py-8">Waiting for duel to initialize...</p>;

  const duelers = [post.author, post.winner];
  const duelComments = comments.filter(c => duelers.includes(c.commenter));
  const lastCommenter = duelComments.length > 0 ? duelComments[duelComments.length - 1].commenter : null;
  const currentTurnUser = lastCommenter === duelers[0] ? duelers[1] : duelers[0];

  const normalizedUser = currentUser?.trim().toLowerCase();
  const normalizedDuelers = duelers.map(d => d?.trim().toLowerCase());
  const canComment = normalizedDuelers.includes(normalizedUser) && normalizedUser === currentTurnUser?.trim().toLowerCase();

  return (
    <PageContainer>
      {post && !post.completed && post.winner && currentUser && currentUser !== post.author && currentUser !== post.winner && (
        <div className="mb-4 flex gap-4">
          {!post.like_users?.includes(currentUser) && (
            <button
              className="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded"
              onClick={async () => {
                try {
                  await request(`/like/${post.id}`, 'POST');
                  toast.success("You liked the winner!");
                  fetchData();
                } catch (err) {
                  toast.error("Failed to like.");
                }
              }}
            >
              👍 Like {post.winner}
            </button>
          )}

          {!post.flag_users?.includes(currentUser) && (
            <button
              className="bg-red-700 hover:bg-red-800 text-white px-4 py-2 rounded"
              onClick={async () => {
                try {
                  await request(`/flag/${post.id}`, 'POST');
                  toast.success("You flagged the winner.");
                  fetchData();
                } catch (err) {
                  toast.error("Failed to flag.");
                }
              }}
            >
              🚩 Flag {post.winner}
            </button>
          )}

          {post.like_users?.includes(currentUser) && (
            <span className="text-green-400">You already liked {post.winner}</span>
          )}

          {post.flag_users?.includes(currentUser) && (
            <span className="text-red-400">You already flagged {post.winner}</span>
          )}
        </div>
      )}

      <div className="max-w-3xl mx-auto">
        <h1 className="text-xl font-bold mb-2 text-[#7FAF92]">Duel in Progress</h1>

        {error && <p className="text-red-400 mb-2">{error}</p>}

        <div className="bg-[#1A2A20] shadow rounded-xl p-4 mb-4">
          <p className="text-sm text-gray-400">
            Posted by <Link to={`/profile/${post.author}`} className="text-[#A1D9B4] hover:underline">{post.author}</Link>
          </p>
          <p className="mt-2 text-lg text-[#E8E5DC]">{post.body}</p>
        </div>

        <div className="bg-[#1F2F25] border border-[#5D749B] rounded-xl p-4 mb-4">
          <p className="text-sm text-[#7FAF92] font-semibold mb-1">Duel Participants:</p>
          <ul className="list-disc list-inside text-sm">
            {duelers.map((user, i) => (
              <li key={i}>
              <Link to={`/profile/${user}`} className="text-[#A1D9B4] hover:underline">{user}</Link>
            </li>
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
                  <strong>
                    <Link to={`/profile/${c.commenter}`} className="text-[#A1D9B4] hover:underline">{c.commenter}</Link>
                  </strong>: {c.text}
                </li>
              ))}
            </ul>
          )}
        </div>

        {canComment && !post.completed && (
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

        {!canComment && !post.completed && duelers.includes(currentUser) && (
          <p className="text-gray-400 italic mt-4">
            Waiting for your turn to comment.
          </p>
        )}

        {!duelers.includes(currentUser) && (
          <p className="text-gray-400 italic mt-4">
            Only duel participants can comment.
          </p>
        )}

        {duelers.includes(currentUser) && !post.completed && (
          <div className="mt-6">
            {(
              (currentUser === post.author && !post.duel_completed_by_author) ||
              (currentUser === post.winner && !post.duel_completed_by_winner)
            ) ? (
              <button
                onClick={handleCompleteDuel}
                className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                ✋ Let’s shake hands and close this
              </button>
            ) : (
              <p className="mt-2 text-sm italic text-yellow-300">
                Waiting for the other duelist to shake hands...
              </p>
            )}
          </div>
        )}
        {post.flag_analysis && (
          <div className="mt-8 bg-[#1A2A20] p-4 rounded-xl shadow space-y-2 border border-[#5D749B]">
            <h3 className="font-semibold text-[#7FAF92]">Flag Analysis</h3>
            <div className="text-sm text-gray-400 space-y-1 mt-2">
              <p>
                🚩 Flags: <strong>{post.flag_analysis.actual_flags}</strong> /
                Required: <strong>{post.flag_analysis.min_flags_required}</strong>
              </p>
              <p>
                👍 Likes: <strong>{post.flag_analysis.actual_likes}</strong> —
                🗳️ Initial Votes: <strong>{post.flag_analysis.initial_votes}</strong>
              </p>
              <p>
                Ratio: <strong>{(post.flag_analysis.flag_ratio * 100).toFixed(1)}%</strong> —
                Net Score: <strong>{post.flag_analysis.net_score}</strong> /
                Threshold: <strong>{post.flag_analysis.threshold_score}</strong>
              </p>
              {post.flag_analysis.actual_flags >= post.flag_analysis.min_flags_required &&
                (post.flag_analysis.flag_ratio > 0.3 || post.flag_analysis.net_score <= post.flag_analysis.threshold_score) && (
                  <p className="text-yellow-400 font-semibold">⚠️ Winner is at risk of being replaced</p>
              )}
            </div>
          </div>
        )}
        {post.completed && (
          <p className="text-yellow-400 mt-6 italic">⚔️ This duel has ended. No more comments, likes or flags allowed.</p>
        )}
      </div>
    </PageContainer>
  );
}
