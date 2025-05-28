import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function CompletedPosts() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/search")
      .then((res) => res.json())
      .then((data) => {
        const completed = data.filter((p) => p.winner);
        setPosts(completed);
      });
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Completed Posts</h1>
      {posts.length === 0 ? (
        <p>No completed posts yet.</p>
      ) : (
        <ul className="space-y-4">
        {posts.map((post) => (
            <li key={post.id || Math.random()} className="border-b pb-2">
            {post.id && post.body ? (
                <>
                <Link to={`/post/${post.id}`} className="text-blue-600 hover:underline">
                    {post.body}
                </Link>
                <p className="text-sm text-green-700 mt-1">
                    🏆 <Link to={`/victory/${post.id}`} className="underline text-green-700 hover:text-green-900">
                    View duel summary
                    </Link>
                </p>
                </>
            ) : (
                <p className="text-red-600 text-sm">Invalid post data</p>
            )}
            </li>
        ))}
        </ul>
      )}
    </div>
  );
}
