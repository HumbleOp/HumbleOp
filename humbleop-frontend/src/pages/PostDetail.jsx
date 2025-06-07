import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import { toast } from 'react-hot-toast';
import PageContainer from '../components/PageContainer';

function formatTimeLeft(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${days}d ${hours}h ${minutes}m ${secs}s`;
}

export default function PostDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const { request, loading, error } = useApi();

  const [currentUser, setCurrentUser] = useState(null);
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [votedFor, setVotedFor] = useState(null);
  const [alreadyCommented, setAlreadyCommented] = useState(false);

  const [endTime, setEndTime] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);

  const fetchDetails = useCallback(async () => {
    try {
      const postData = await request(`/status/${id}`);
      const commentData = await request(`/comments/${id}`);
      setPost(postData);
      setComments(commentData.comments || []);

      if (postData.voting_ends_in != null && postData.voting_ends_in > 0) {
        setEndTime(Date.now() + postData.voting_ends_in * 1000);
      } else {
        setEndTime(null);
      }

      if (token && postData.author) {
        const res = await fetch('http://localhost:5000/profile', {
          headers: { 'Authorization': 'Bearer ' + token }
        });
        const userData = await res.json();
        setCurrentUser(userData.username);

        const votedComment = (commentData.comments || []).find(c =>
          c.voters?.includes(userData.username)
        );
        if (votedComment) setVotedFor(votedComment.commenter);

        const hasCommented = (commentData.comments || []).some(c =>
          c.commenter === userData.username
        );
        setAlreadyCommented(hasCommented);
      }
    } catch {
      // handle errors
    }
  }, [id, token, request]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  useEffect(() => {
    if (endTime == null) return;
    const initialLeft = Math.max(Math.floor((endTime - Date.now()) / 1000), 0);
    setTimeLeft(initialLeft);

    const intervalId = setInterval(() => {
      const diff = Math.max(Math.floor((endTime - Date.now()) / 1000), 0);
      setTimeLeft(diff);
      if (diff <= 0) {
        clearInterval(intervalId);
        fetchDetails();
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, [endTime, fetchDetails]);

  async function handleCommentSubmit(e) {
    e.preventDefault();
    try {
      await request(`/comment/${id}`, 'POST', { text: commentText });
      toast.success('Comment submitted!');
      setCommentText('');
      fetchDetails();
    } catch (err) {
      toast.error(err.message || 'Failed to comment');
    }
  }

  async function handleVote(candidate) {
    try {
      await request(`/vote/${id}`, 'POST', { candidate });
      toast.success(`Voted for ${candidate}`);
      fetchDetails();
    } catch (err) {
      toast.error(err.message || 'Vote failed');
    }
  }

  async function handleUnvote() {
    try {
      const res = await fetch(`http://localhost:5000/unvote/${id}`, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token }
      });
      const data = await res.json();
      if (res.ok) {
        toast.success('Vote revoked');
        setVotedFor(null);
        fetchDetails();
      } else {
        toast.error(data.error || 'Unvote failed');
      }
    } catch (err) {
      toast.error(err.message || 'Unvote failed');
    }
  }

  if (loading || !post) return <p className="text-center text-white py-8">Loading post...</p>;
  if (error) return <p className="text-red-400 text-center py-8">{error}</p>;

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto px-4 py-6">
        <h2 className="text-lg font-bold mb-2 text-[#7FAF92]">
          Post by{' '}
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
            className="text-xl font.bold text-[#A1D9B4] hover:underline"
          >
            {post.author}
          </Link>
          <div className="mb-4 bg-black border border-white p-4 rounded">
          <p className="text-sm text-gray-400">
          Posted on {post.created_at ? new Date(post.created_at).toLocaleString(): '—'}
        </p>
        </div>


        </h2>
        <div className="mb-4 bg-black border border-white p-4 rounded">
          <p className="antialiased mb-4 text-2xl font-mono text-[#ebebeb]">{post.body}</p>
        </div>
        {/* Media, results and duel link */}
        <div className="mb-6 space-y-1">
          <p>
            <strong className="text-[#5D749B]">Winner:</strong>{' '}
            {post.winner ? (
              <Link to={`/profile/${post.winner}`} className="text-[#A1D9B4] hover:underline">
                {post.winner}
              </Link>
            ) : '—'}
          </p>
          <p>
            <strong className="text-[#5D749B]">Second:</strong>{' '}
            {post.second ? (
              <Link to={`/profile/${post.second}`} className="text-[#A1D9B4] hover:underline">
                {post.second}
              </Link>
            ) : '—'}
          </p>
          {!post.started && (
            <p className="text-[#E8E5DC]">
              <strong className="text-[#5D749B]">Votes end in:</strong>{' '}
              <span className="text-yellow-400">{timeLeft != null ? formatTimeLeft(timeLeft) : '—'}</span>
            </p>
          )}
          {post.started && post.winner && post.second && (
            <p className="text-sm text-yellow-400">
              <Link to={`/duel/${post.id}`} className="underline hover:text-yellow-200">👉 Go to duel</Link>
            </p>
          )}
        </div>

        {/* Comments Section */}
        <h3 className="text-lg font-semibold mb-2 text-[#7FAF92]">Comments</h3>
        {comments.length === 0 ? (
          <p className="italic text-gray-400">No comments yet.</p>
        ) : (
          <ul className="space-y-3">
            {comments.map((c, i) => (
              <li key={i} className="border border-[#5D749B] p-3 rounded">
                <strong>
                  <Link to={`/profile/${c.commenter}`} className="text-[#A1D9B4] hover:underline">
                    {c.commenter}
                  </Link>:
                </strong>
                <span className="ml-1 text-[#E8E5DC]">{c.text}</span>
                <span className="text-gray-400"> ({c.votes} votes)</span>
                {!post.started && !post.completed && token && currentUser && currentUser !== post.author && currentUser !== c.commenter && (
                  votedFor === null ? (
                    <button onClick={() => handleVote(c.commenter)} className="ml-4 text-sm bg-[#7FAF92] text-[#E8E5DC] px-2 py-1 rounded hover:bg-[#5D749B]">
                      Vote
                    </button>
                  ) : votedFor === c.commenter ? (
                    <>
                      <span className="ml-4 text-green-400">🗳️ You voted</span>
                      <button onClick={handleUnvote} className="ml-2 text-sm text-white bg-[#a32303] px-2 py-1 rounded hover:bg-[#a32303]">
                        Unvote
                      </button>
                    </>
                  ) : null
                )}
              </li>
            ))}
          </ul>
        )}

        {/* Comment Form or Messages */}
        {!post.started && !post.completed && token && currentUser && currentUser !== post.author && (
          alreadyCommented ? (
            <p className="mt-6 italic text-yellow-400">💬 You already commented on this post.</p>
          ) : (
            <form onSubmit={handleCommentSubmit} className="mt-6">
              <h4 className="mb-2 text-[#5D749B] font-semibold">Leave a comment</h4>
              <textarea
                value={commentText}
                onChange={e => setCommentText(e.target.value)}
                rows={4}
                className="w-full p-2 border rounded bg-[#16221C] text-[#E8E5DC]"
                placeholder="Write your comment..."
              />
              <button type="submit" className="mt-2 bg-[#7FAF92] text-[#E8E5DC] px-4 py-2 rounded hover:bg-[#5D749B]">
                Submit
              </button>
            </form>
          )
        )}

        {!post.started && !post.completed && token && currentUser === post.author && (
          <p className="mt-6 italic text-red-400">You cannot comment on your own post.</p>
        )}

        {post.started && !post.completed && token && currentUser !== post.author && (
          <p className="mt-6 italic text-yellow-400">🥊 Duel in progress. You can no longer comment.</p>
        )}

        {post.completed && (
          <p className="text-yellow-400 mt-6 italic text-center">
            🤝 Hands shaken by both! The duel is now complete. No more comments, likes or flags allowed.
          </p>
        )}
      </div>
    </PageContainer>
  );
}
