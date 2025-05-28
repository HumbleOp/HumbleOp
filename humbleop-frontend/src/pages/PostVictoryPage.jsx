import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function PostVictoryPage() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [winnerComment, setWinnerComment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [likeCount, setLikeCount] = useState(0);
  const [flagCount, setFlagCount] = useState(0);
  const [likeUsers, setLikeUsers] = useState([]);
  const [flagUsers, setFlagUsers] = useState([]);
  const [ranking, setRanking] = useState({});


  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`http://localhost:5000/status/${id}`);
      const data = await res.json();
      setPost(data.post);
      setWinnerComment(data.comments?.find(c => c.commenter === data.winner) || null);
      setLikeCount(data.likes || 0);
      setFlagCount(data.flags || 0);
      setLikeUsers(data.like_users || []);
      setFlagUsers(data.flag_users || []);
      setRanking(data.ranking || {});
      setLoading(false);
      };
    fetchData();
  }, [id]);

  if (loading) return <p className="text-center p-4">Loading duel summary...</p>;
  if (!post || !winnerComment) return <p className="text-center p-4">Post or winner not found.</p>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-2">Duel Summary</h1>

      <div className="bg-white shadow-md rounded-xl p-4 mb-4">
        <p className="text-sm text-gray-500">Posted by <strong>{post.author}</strong></p>
        <p className="mt-2 text-lg">{post.body}</p>
      </div>

      <div className="bg-green-50 border border-green-300 rounded-xl p-4 mb-4">
        <p className="text-sm text-gray-500">Winner: <strong>{winnerComment.commenter}</strong></p>
        <p className="mt-2 italic">{winnerComment.text}</p>
      </div>

      <div className="flex items-center gap-6 mt-2">
        <p>👍 Likes: {likeCount}</p>
        <p>🚩 Flags: {flagCount}</p>
      </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-4">
        <div>
            <h2 className="font-semibold">Who liked:</h2>
            <ul className="list-disc list-inside text-sm text-gray-700">
            {likeUsers.length === 0 ? <li>No likes yet.</li> : likeUsers.map(u => <li key={u}>{u}</li>)}
            </ul>
        </div>

        <div>
            <h2 className="font-semibold">Who flagged:</h2>
            <ul className="list-disc list-inside text-sm text-gray-700">
            {flagUsers.length === 0 ? <li>No flags yet.</li> : flagUsers.map(u => <li key={u}>{u}</li>)}
            </ul>
        </div>

        <div className="sm:col-span-2">
            <h2 className="font-semibold mt-4">Voting Summary:</h2>
            {Object.keys(ranking).length === 0 ? (
            <p className="text-sm text-gray-600">No votes recorded.</p>
            ) : (
            <ul className="list-disc list-inside text-sm text-gray-700">
                {Object.entries(ranking)
                .sort((a, b) => b[1] - a[1])
                .map(([user, count]) => (
                    <li key={user}>
                    {user} — {count} vote{count > 1 ? 's' : ''}
                    </li>
                ))}
            </ul>
            )}
        </div>
        </div>


      {/* Qui potremmo aggiungere in seguito i commenti degli utenti terzi */}
    </div>
  );
}
