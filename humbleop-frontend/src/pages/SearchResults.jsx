// src/pages/SearchResults.jsx
import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import PageContainer from "../components/PageContainer";

export default function SearchResults() {
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState({ users: [], posts: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");
  const { token } = useAuth();
  const [currentUser, setCurrentUser] = useState(null);


  const q = searchParams.get("q") || "";

  useEffect(() => {
    async function fetchResults() {
            if (token) {
        fetch("http://localhost:5000/profile", {
          headers: { Authorization: "Bearer " + token }
        })
          .then(res => res.json())
          .then(data => setCurrentUser(data.username));
      }
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:5000/search?q=${encodeURIComponent(q)}&type=all&limit=20&sort=desc`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Search failed");
        setResults(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (q.trim()) {
      fetchResults();
    }
  }, [q]);

  function highlight(text) {
    if (!q.trim()) return text;
    const regex = new RegExp(`(${q})`, "gi");
    return text.split(regex).map((part, i) =>
      regex.test(part) ? <mark key={i} className="bg-yellow-400 text-black">{part}</mark> : part
    );
  }

  if (!q.trim()) return <p className="p-4 text-[#E8E5DC] bg-[#101B13] min-h-screen">Please enter a search query.</p>;
  if (loading) return <p className="p-4 text-[#E8E5DC] bg-[#101B13] min-h-screen">Searching for &quot;{q}&quot;...</p>;
  if (error) return <p className="p-4 text-red-600 bg-[#101B13] min-h-screen">Error: {error}</p>;

  return (
    <PageContainer>
      <div className="w-full max-w-3xl bg-[#1A2A20] p-6 rounded shadow">
        <h1 className="text-2xl font-bold mb-6 text-[#7FAF92]">Search Results for &quot;{q}&quot;</h1>

        <div className="flex gap-2 mb-6">
          <button onClick={() => setFilter("all")} className={`px-3 py-1 rounded ${filter === "all" ? "bg-[#7FAF92] text-[#E8E5DC]" : "bg-[#2F3F30] text-[#E8E5DC]"}`}>All</button>
          <button onClick={() => setFilter("users")} className={`px-3 py-1 rounded ${filter === "users" ? "bg-[#7FAF92] text-[#E8E5DC]" : "bg-[#2F3F30] text-[#E8E5DC]"}`}>Users</button>
          <button onClick={() => setFilter("posts")} className={`px-3 py-1 rounded ${filter === "posts" ? "bg-[#7FAF92] text-[#E8E5DC]" : "bg-[#2F3F30] text-[#E8E5DC]"}`}>Posts</button>
        </div>

        {(filter === "all" || filter === "users") && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-[#7FAF92] mb-2">Users</h2>
            {results.users.length === 0 ? (
              <p className="text-sm text-gray-400">No users found.</p>
            ) : (
              <ul className="list-disc list-inside">
                {results.users.map((u) => (
                  <li key={u}>
                    <Link
                      to={currentUser === u ? '/profile' : `/profile/${u}`}
                      className="text-[#A1D9B4] hover:underline"
                    >
                      {highlight(u)}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {(filter === "all" || filter === "posts") && (
          <div>
            <h2 className="text-lg font-semibold text-[#7FAF92] mb-2">Posts</h2>
            {results.posts.length === 0 ? (
              <p className="text-sm text-gray-400">No posts found.</p>
            ) : (
              <ul className="space-y-4">
                {results.posts.map((post) => (
                  <li key={post.id} className="border-b border-[#3A4B3C] pb-2">
                    <Link to={`/post/${post.id}`} className="text-[#A1D9B4] hover:underline">
                      {highlight(post.body.length > 100 ? post.body.slice(0, 100) + "..." : post.body)}
                    </Link>
                    <p className="text-sm text-gray-400">by {post.author}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </PageContainer>
  );
}
