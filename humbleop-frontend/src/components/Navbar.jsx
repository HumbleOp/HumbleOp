// src/components/Navbar.jsx
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useEffect, useState } from "react";
import logo from "../assets/logo_img.png";

export default function Navbar() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [query, setQuery] = useState("");
  const [placeholder, setPlaceholder] = useState("");


    function handleSearch(e) {
    e.preventDefault();
    if (query.trim()) {
        navigate(`/search?q=${encodeURIComponent(query.trim())}`);
        setQuery("");
    }
    }

useEffect(() => {
  const text = "Search debates...";
  let i = 0;

  const interval = setInterval(() => {
    setPlaceholder(text.slice(0, i));
    i++;
    if (i > text.length) clearInterval(interval);
  }, 70);

  return () => clearInterval(interval);
}, []);


  useEffect(() => {
    async function fetchProfile() {
      if (!token) return;
      const res = await fetch("http://localhost:5000/profile", {
        headers: { Authorization: "Bearer " + token },
      });
      const data = await res.json();
      if (res.ok && data.username) setUsername(data.username);
    }
    fetchProfile();
  }, [token]);

  return (
    <nav className="flex items-center justify-between px-6 py-3 bg-white shadow border-b sticky top-0 z-50">
      <div className="flex gap-4 items-center">
        <Link to="/posts" className="flex items-center gap-2">
          <img src={logo} alt="HumbleOp Logo" className="h-8 w-10" />
          <span className="text-xl font-bold text-blue-700">HumbleOp</span>
        </Link>
        <NavLink
          to="/posts"
          className={({ isActive }) =>
            isActive ? "text-blue-900 font-semibold" : "text-blue-700 hover:underline"
          }
        >
          All Posts
        </NavLink>
        <NavLink
          to="/completed"
          className={({ isActive }) =>
            isActive ? "text-blue-900 font-semibold" : "text-blue-700 hover:underline"
          }
        >
          Completed
        </NavLink>
        {token && (
          <>
            <NavLink
              to="/create"
              className={({ isActive }) =>
                isActive ? "text-blue-900 font-semibold" : "text-blue-700 hover:underline"
              }
            >
              New Post
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                isActive ? "text-blue-900 font-semibold" : "text-blue-700 hover:underline"
              }
            >
              Profile
            </NavLink>
          </>
        )}
      </div>

      {token && (
        <div className="flex items-center gap-3 text-sm text-gray-700">
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={placeholder}
                className="border px-2 py-1 rounded text-black"
            />
            <button
                type="submit"
                className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
            >
                Go
            </button>
            </form>
          <span>{username}</span>
          <button
            onClick={() => {
              logout();
              navigate("/");
            }}
            className="text-red-600 hover:underline"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}