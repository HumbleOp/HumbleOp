import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function PostVictoryPage() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [winnerComment, setWinnerComment] = useState(null);
  const [ranking, setRanking] = useState({});
  const [likeUsers, setLikeUsers] = useState([]);
  const [flagUsers, setFlagUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [secondUser, setSecondUser] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`http://localhost:5000/status/${id}`);
      const data = await res.json();

      const winner = data.winner;
      const winnerComment = winner
        ? data.comments?.find(c => c.commenter === winner) || null
        : null;

      setPost(data);
      setWinnerComment(winnerComment);
      setLikeUsers(data.like_users || []);
      setFlagUsers(data.flag_users || []);
      setRanking(data.ranking || {});
      setLoading(false);
    };
    fetchData();
  }, [id]);


  if (loading) return <p className="text-center p-4">Loading duel summary...</p>;
  if (!post) return <p className="text-center p-4">Post not found.</p>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Duel Summary</h1>

      <div className="bg-white shadow-md rounded-xl p-4 mb-4">
        <p className="text-sm text-gray-500">Posted by <strong>{post.author}</strong></p>
        <p className="mt-2 text-lg">{post.body}</p>
      </div>

      {post.winner && winnerComment && (
        <div className="bg-green-50 border border-green-300 rounded-xl p-4 mb-4">
          <p className="text-sm text-gray-500">Winner: <strong>{winnerComment.commenter}</strong></p>
          <blockquote className="mt-2 italic"> {winnerComment.text} </blockquote>
        </div>
      )}

      {secondUser && (
        <p className="text-sm text-blue-700 mb-2">Second place: <strong>{secondUser}</strong></p>
      )}

      <div className="flex items-center gap-6 mt-2">
        <p>👍 Likes: {likeUsers.length}</p>
        <p>🚩 Flags: {flagUsers.length}</p>
      </div>

      <div className="mt-4">
        <h2 className="font-semibold">Who liked:</h2>
        <ul className="list-disc list-inside text-sm text-gray-700">
          {likeUsers.length === 0 ? <li>No likes yet.</li> :
            likeUsers.map((u, idx) => <li key={`like-${u}-${idx}`}>{u}</li>)}
        </ul>
      </div>

      <div className="mt-4">
        <h2 className="font-semibold">Who flagged:</h2>
        <ul className="list-disc list-inside text-sm text-gray-700">
          {flagUsers.length === 0 ? <li>No flags yet.</li> :
            flagUsers.map((u, idx) => <li key={`flag-${u}-${idx}`}>{u}</li>)}
        </ul>
      </div>

      <div className="mt-6">
        <h2 className="font-semibold">Voting Summary:</h2>
        {Object.keys(ranking).length === 0 ? (
          <p className="text-sm text-gray-600">No votes recorded.</p>
        ) : (
          <ul className="list-disc list-inside text-sm text-gray-700">
            {Object.entries(ranking)
              .sort((a, b) => b[1] - a[1])
              .map(([user, count]) => (
                <li key={`rank-${user}`}>{user} — {count} vote{count !== 1 ? "s" : ""}</li>
              ))}
          </ul>
        )}
      </div>
    </div>
  );
}
