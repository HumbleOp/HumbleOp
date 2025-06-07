// src/pages/PostList.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../context/AuthContext';
import PageContainer from '../components/PageContainer';

// --- Helper: format seconds into "Xd Xh Xm Xs" ---
function formatTimeLeft(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${days}d ${hours}h ${minutes}m ${secs}s`;
}

export default function PostList() {
  const { request, loading, error } = useApi();
  const [posts, setPosts] = useState([]);
  const { token } = useAuth();
  const [currentUser, setCurrentUser] = useState(null);

  // 1) Fetch posts on mount, and initialize endTime & timeLeft for each post
  useEffect(() => {
    async function fetchPosts() {
      try {
        const data = await request('/search?q=&type=post&limit=20&sort=desc');
        const fetchedPosts = data.posts || [];

        // Compute endTime (timestamp in ms) and initial timeLeft (seconds) for each post
        const now = Date.now();
        const postsWithTimers = fetchedPosts.map(post => {
          if (post.voting_ends_in != null) {
            return {
              ...post,
              endTime: now + post.voting_ends_in * 1000,
              timeLeft: post.voting_ends_in
            };
          } else {
            return {
              ...post,
              endTime: null,
              timeLeft: null
            };
          }
        });

        setPosts(postsWithTimers);

        // If user is logged in, fetch their username
        if (token) {
          const res = await fetch('http://localhost:5000/profile', {
            headers: { Authorization: 'Bearer ' + token }
          });
          const user = await res.json();
          setCurrentUser(user.username);
        }
      } catch {
        // Errors are handled by useApi
      }
    }

    fetchPosts();
  }, [request, token]);

  // 2) Set up a global interval that ticks every second and updates timeLeft
  useEffect(() => {
    if (posts.length === 0) return;

    const intervalId = setInterval(() => {
      setPosts(prevPosts =>
        prevPosts.map(post => {
          // If there's no endTime, leave it untouched
          if (post.endTime == null) return post;

          const diffSeconds = Math.max(
            Math.floor((post.endTime - Date.now()) / 1000),
            0
          );
          return { ...post, timeLeft: diffSeconds };
        })
      );
    }, 1000);

    return () => clearInterval(intervalId);
  }, [posts]);

  if (loading) {
    return (
      <PageContainer>
        <p className="text-center text-white py-8">Loading posts...</p>
      </PageContainer>
    );
  }
  if (error) {
    return (
      <PageContainer>
        <p className="text-center text-red-400 py-8">{error}</p>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-[#7FAF92] mb-4">All Posts</h1>

        {posts.length === 0 ? (
          <p className="text-gray-400 italic">No posts found.</p>
        ) : (
          <ul className="space-y-4">
            {posts.map(post => {
              // Determine post status
              const duelCompleted    = post.timeLeft === 0 && Boolean(post.winner);
              const duelInProgress = !duelCompleted && Boolean(post.winner);
              const votingInProgress = !post.winner && !post.completed;

              // Background color classes
              let bgClass = 'bg-[#1A2A20]'; // fallback dark
              if (duelCompleted) {
                bgClass = 'bg-[#41116b]';
              } else if (duelInProgress) {
                bgClass = 'bg-[#a03809]';
              } else if (votingInProgress) {
                bgClass = 'bg-[#063835]';
              }

              // Truncate body to 200 chars
              const previewText =
                post.body.length > 200 ? post.body.slice(0, 200) + '...' : post.body;

              return (
                <li
                  key={post.id}
                  className={`${bgClass} p-4 rounded shadow hover:shadow-md transition`}
                >
                  <Link
                    to={`/post/${post.id}`}
                    className="text-lg font-semibold text-[#E8E5DC] hover:text-[#7FAF92]"
                  >
                    {previewText}
                  </Link>
                  <p className="text-sm text-gray-400 mt-1">
                    by{' '}
                    <div className="flex items-center gap-2 mb-4">
                      <img
                        src={`http://localhost:5000${post.author_avatar}`}
                        alt={`${post.author} avatar`}
                        className="w-10 h-10 rounded-full"
                      />
                      <span>{post.author}</span>
                    </div>
                    <Link
                      to={currentUser === post.author ? '/profile' : `/profile/${post.author}`}
                      className="text-[#A1D9B4] hover:underline"
                    >
                      {post.author}
                    </Link>
                  </p>
                    <p className="text-sm text-gray-400 mt-1">
                      Posted on {post.created_at
                        ? new Date(post.created_at).toLocaleString()
                        : '—'}
                    </p>
                  <div className="mt-2 flex flex-col space-y-2">
                    {/* Voting in progress: show badge + live countdown */}
                    {votingInProgress && (
                      <div className="flex items-center space-x-2">
                        <span className="inline-block px-2 py-1 bg-green-600 text-white text-xs font-semibold rounded">
                          Voting in progress
                        </span>
                        {post.timeLeft > 0 ? (
                          <span className="text-yellow-400 text-sm font-mono">
                            {formatTimeLeft(post.timeLeft)}
                          </span>
                        ) : (
                          <span className="text-red-400 text-sm font-semibold">
                            Voting closed
                          </span>
                        )}
                      </div>
                    )}

                    {/* Duel ongoing: show winner/second and badge */}
                    {duelInProgress && (
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <p className="text-sm text-gray-200">
                            <span className="text-yellow-400 font-semibold">🏆 Winner:</span>{' '}
                            {post.winner ? (
                              <Link
                                to={
                                  currentUser === post.winner ? '/profile' : `/profile/${post.winner}`
                                }
                                className="text-[#A1D9B4] hover:underline"
                              >
                                {post.winner}
                              </Link>
                            ) : (
                              '—'
                            )}
                          </p>
                          <p className="text-sm text-gray-200 mt-1">
                            <span className="text-gray-400 font-semibold">🥈 Second:</span>{' '}
                            {post.second ? (
                              <Link
                                to={
                                  currentUser === post.second
                                    ? '/profile'
                                    : `/profile/${post.second}`
                                }
                                className="text-[#A1D9B4] hover:underline"
                              >
                                {post.second}
                              </Link>
                            ) : (
                              '—'
                            )}
                          </p>
                        </div>
                        <span className="inline-block px-2 py-1 bg-yellow-600 text-black text-xs font-semibold rounded">
                          Duel ongoing
                        </span>
                      </div>
                    )}

                    {/* Duel completed: show winner/second and badge */}
                    {duelCompleted && (
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <p className="text-sm text-gray-200">
                            <span className="text-yellow-400 font-semibold">🏆 Winner:</span>{' '}
                            {post.winner ? (
                              <Link
                                to={
                                  currentUser === post.winner ? '/profile' : `/profile/${post.winner}`
                                }
                                className="text-[#A1D9B4] hover:underline"
                              >
                                {post.winner}
                              </Link>
                            ) : (
                              '—'
                            )}
                          </p>
                          <p className="text-sm text-gray-200 mt-1">
                            <span className="text-gray-400 font-semibold">🥈 Second:</span>{' '}
                            {post.second ? (
                              <Link
                                to={
                                  currentUser === post.second
                                    ? '/profile'
                                    : `/profile/${post.second}`
                                }
                                className="text-[#A1D9B4] hover:underline"
                              >
                                {post.second}
                              </Link>
                            ) : (
                              '—'
                            )}
                          </p>
                        </div>
                        <span className="inline-block px-2 py-1 bg-gray-500 text-white text-xs font-semibold rounded">
                          Duel completed
                        </span>
                      </div>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </PageContainer>
  );
}
