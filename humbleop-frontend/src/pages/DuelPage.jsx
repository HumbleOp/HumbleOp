import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function DuelPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [text, setText] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchData = useCallback(async () => {
    if (!token) return;

    try {
      const resPost = await fetch(`http://localhost:5000/status/${id}`);
      const postData = await resPost.json();

      if (!resPost.ok) throw new Error(postData.error);

      const resComments = await fetch(`http://localhost:5000/comments/${id}`);
      const commentData = await resComments.json();

      const resProfile = await fetch("http://localhost:5000/profile", {
        headers: { Authorization: "Bearer " + token },
      });
      const profileData = await resProfile.json();

      setPost(postData);
      setComments(commentData.comments || []);
      setCurrentUser(profileData.username);

      if (!postData.started) {
        navigate(`/victory/${id}`);
      }
    } catch (err) {
      setError(err.message);
    }
  }, [id, token, navigate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      const res = await fetch(`http://localhost:5000/comment/${id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess("Comment submitted!");
        setText("");
        setComments([...comments, { commenter: currentUser, text, votes: 0 }]);
      } else {
        setError(data.error || "Failed to comment");
      }
    } catch (err) {
      setError(err.message);
    }
  }

  if (!post) return <p>Loading duel...</p>;

  const duelers = [post.winner, post.second];
  const canComment = duelers.includes(currentUser);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-2">Duel in Progress</h1>

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
          <button type="submit" className="mt-2 bg-blue-600 text-white px-4 py-2 rounded">
            Send
          </button>
          {error && <p className="text-red-600 mt-1">{error}</p>}
          {success && <p className="text-green-600 mt-1">{success}</p>}
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
