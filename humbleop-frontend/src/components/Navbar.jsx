// src/components/Navbar.jsx
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useEffect, useState } from "react";

export default function Navbar() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");

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
        <NavLink to="/posts" className="text-xl font-bold text-blue-700">
          HumbleOp
        </NavLink>
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
