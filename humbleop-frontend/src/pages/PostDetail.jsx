import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';

export default function PostDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const { request, loading, error } = useApi();

  const [currentUser, setCurrentUser] = useState(null);
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [commentError, setCommentError] = useState('');
  const [commentSuccess, setCommentSuccess] = useState('');
  const [votedFor, setVotedFor] = useState(null);
  const [voteStatus, setVoteStatus] = useState('');

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
      }
    } catch {
        // error already handled by useApi
    }
  }, [id, token, request]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  async function handleCommentSubmit(e) {
    e.preventDefault();
    setCommentError('');
    setCommentSuccess('');

    try {
      await request(`/comment/${id}`, 'POST', { text: commentText });
      setCommentSuccess('Comment submitted!');
      setCommentText('');
      fetchDetails();
    } catch (err) {
      setCommentError(err.message);
    }
  }

  async function handleVote(candidate) {
    setVoteStatus('');
    try {
      await request(`/vote/${id}`, 'POST', { candidate });
      setVoteStatus(`Voted for ${candidate}`);
      fetchDetails();
    } catch (err) {
      setVoteStatus(err.message);
    }
  }


  if (loading || !post) return <p>Loading post...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;


  return (
    <div>
      <h2>Post by {post.author}</h2>
      <p>{post.body}</p>

      {post.media?.length > 0 && (
        <div>
          <strong>Media:</strong>
          <ul>
            {post.media.map((url, index) => (
              <li key={index}><a href={url} target="_blank" rel="noreferrer">{url}</a></li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <p><strong>Winner:</strong> {post.winner || '—'}</p>
        <p><strong>Second:</strong> {post.second || '—'}</p>
        <p><strong>Votes end in:</strong> {post.voting_ends_in} seconds</p>
        {post.winner && post.second && post.started && (
          <p className="mt-2 text-sm text-yellow-700">
            <Link to={`/duel/${post.id}`} className="underline hover:text-yellow-900">
              👉 Go to duel
            </Link>
          </p>
        )}
      </div>

      <h3>Comments</h3>
      {comments.length === 0 ? (
        <p>No comments yet.</p>
      ) : (
        <ul>
          {comments.map((c, i) => (
            <li key={i}>
              <strong>{c.commenter}:</strong> {c.text} ({c.votes} votes)
              {token && currentUser && currentUser !== post.author && currentUser !== c.commenter && (
                votedFor === null ? (
                  <button onClick={() => handleVote(c.commenter)}>Vote</button>
                ) : votedFor === c.commenter ? (
                  <span style={{ marginLeft: '1em', color: 'green' }}>🗳️ You voted for this comment</span>
                ) : null
              )}
            </li>
          ))}
        </ul>
      )}

      {voteStatus && <p>{voteStatus}</p>}

      {token && currentUser && currentUser !== post.author && (
        <form onSubmit={handleCommentSubmit} style={{ marginTop: '1em' }}>
          <h4>Leave a comment</h4>
          <textarea
            value={commentText}
            onChange={e => setCommentText(e.target.value)}
            rows={4}
            style={{ width: '100%' }}
            placeholder="Write your comment..."
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Submitting...' : 'Submit'}
          </button>
          {commentError && <p style={{ color: 'red' }}>{commentError}</p>}
          {commentSuccess && <p style={{ color: 'green' }}>{commentSuccess}</p>}
        </form>
      )}

      {token && currentUser === post.author && (
        <p>You cannot comment on your own post.</p>
      )}
    </div>
  );
}
