// src/pages/PostDetail.jsx
import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import { toast } from 'react-hot-toast';
import PageContainer from '../components/PageContainer';

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


  const fetchDetails = useCallback(async () => {
    try {
      const postData = await request(`/status/${id}`);
      const commentData = await request(`/comments/${id}`);

      setPost(postData);
      setComments(commentData.comments || []);
      if (token && postData.author) {
        const res = await fetch('http://localhost:5000/profile', {
          headers: { 'Authorization': 'Bearer ' + token }
        });
        const userData = await res.json();
        setCurrentUser(userData.username);

        const votedComment = commentData.comments.find(c =>
          c.voters?.includes(userData.username)
        );
        if (votedComment) {
          setVotedFor(votedComment.commenter);
        }

        const hasCommented = commentData.comments.some(c =>
          c.commenter === userData.username
        );
        setAlreadyCommented(hasCommented);
      }

    } catch {
        // error handled by useApi
    }
  }, [id, token, request]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

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
        headers: {
          'Authorization': 'Bearer ' + token
        }
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
        <h2 className="text-xl font-bold mb-2 text-[#7FAF92]">
          <h2 className="text-xl font-bold mb-2 text-[#7FAF92]">
            Post by <Link to={currentUser === post.author ? '/profile' : `/profile/${post.author}`} className="text-[#A1D9B4] hover:underline">{post.author}</Link>
          </h2>
        </h2>
        <p className="mb-4">{post.body}</p>

        {post.media?.length > 0 && (
          <div className="mb-4">
            <strong className="text-[#5D749B]">Media:</strong>
            <ul className="list-disc list-inside">
              {post.media.map((url, index) => (
                <li key={index}>
                  <a href={url} target="_blank" rel="noreferrer" className="text-blue-300 underline">{url}</a>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mb-6 space-y-1">
          <p><strong className="text-[#5D749B]">Winner:</strong> {
            post.winner ? (
              <Link to={currentUser === post.winner ? '/profile' : `/profile/${post.winner}`} className="text-[#A1D9B4] hover:underline">{post.winner}</Link>
            ) : '—'
          }</p>

          <p><strong className="text-[#5D749B]">Second:</strong> {
            post.second ? (
              <Link to={currentUser === post.second ? '/profile' : `/profile/${post.second}`} className="text-[#A1D9B4] hover:underline">{post.second}</Link>
            ) : '—'
          }</p>

          <p><strong className="text-[#5D749B]">Votes end in:</strong> {post.voting_ends_in} seconds</p>
          {post.winner && post.second && post.started && (
            <p className="text-sm text-yellow-400">
              <Link to={`/duel/${post.id}`} className="underline hover:text-yellow-200">
                👉 Go to duel
              </Link>
            </p>
          )}
        </div>

        <h3 className="text-lg font-semibold mb-2 text-[#7FAF92]">Comments</h3>
        {comments.length === 0 ? (
          <p className="italic text-gray-400">No comments yet.</p>
        ) : (
          <ul className="space-y-3">
            {comments.map((c, i) => (
              <li key={i} className="border border-[#5D749B] p-3 rounded">
                <strong>
                  <Link to={currentUser === c.commenter ? '/profile' : `/profile/${c.commenter}`} className="text-[#A1D9B4] hover:underline">
                    {c.commenter}
                  </Link>:
                </strong>
                 {c.text} <span className="text-sm text-gray-400">({c.votes} votes)</span>
                {!post.completed && token && currentUser && currentUser !== post.author && currentUser !== c.commenter && (
                  votedFor === null ? (
                    <button
                      onClick={() => handleVote(c.commenter)}
                      className="ml-4 text-sm bg-[#7FAF92] text-black px-2 py-1 rounded hover:bg-[#5D749B]"
                    >
                      Vote
                    </button>
                  ) : votedFor === c.commenter ? (
                    <>
                      <span className="ml-4 text-green-400">🗳️ You voted</span>
                      <button
                        onClick={handleUnvote}
                        className="ml-2 text-sm text-white bg-red-600 px-2 py-1 rounded hover:bg-red-800"
                      >
                        Unvote
                      </button>
                    </>
                  ) : null
                )}
              </li>
            ))}
          </ul>
        )}
        {token && currentUser && currentUser !== post.author && !post.started && !post.completed && (
          alreadyCommented ? (
            <p className="mt-6 italic text-yellow-400 text-center">💬 You already commented on this post.</p>
          ) : (
            <form onSubmit={handleCommentSubmit} className="mt-6">
              <h4 className="mb-2 text-[#5D749B] font-semibold">Leave a comment</h4>
              <textarea
                value={commentText}
                onChange={e => setCommentText(e.target.value)}
                rows={4}
                className="w-full p-2 border rounded text-black"
                placeholder="Write your comment..."
              />
              <button
                type="submit"
                className="mt-2 bg-[#7FAF92] text-black px-4 py-2 rounded hover:bg-[#5D749B]"
              >
                Submit
              </button>
            </form>
          )
        )}
        {token && !post.completed && currentUser && currentUser !== post.author && post.started && (
          <p className="mt-6 italic text-yellow-400">🥊 Duel in progress. You can no longer comment.</p>
        )}

        {token && !post.completed && currentUser === post.author && (
          <p className="mt-6 text-gray-400 italic">You cannot comment on your own post.</p>
        )}
      </div>
       {post.completed && (
          <p className="text-yellow-400 mt-6 italic text-center">⚔️ This duel has ended. No more comments, likes or flags allowed.</p>
        )}
    </PageContainer>
  );
}
