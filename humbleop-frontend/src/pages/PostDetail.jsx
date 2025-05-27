import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function PostDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const [currentUser, setCurrentUser] = useState(null);
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [error, setError] = useState('');
  const [commentText, setCommentText] = useState('');
  const [commentError, setCommentError] = useState('');
  const [commentSuccess, setCommentSuccess] = useState('');
  const [votedFor, setVotedFor] = useState(null);
  const [voteStatus, setVoteStatus] = useState('');

  useEffect(() => {
    fetchDetails();
  }, [id]);

  async function fetchDetails() {
    try {
      const resPost = await fetch(`http://localhost:5000/status/${id}`);
      const resComments = await fetch(`http://localhost:5000/comments/${id}`);
      const postData = await resPost.json();
      const commentData = await resComments.json();

      if (resPost.ok) setPost(postData);
      else setError(postData.error || 'Failed to load post');

      if (resComments.ok) setComments(commentData.comments || []);

      if (token && postData.author) {
        const res = await fetch('http://localhost:5000/profile', {
          headers: { 'Authorization': 'Bearer ' + token }
        });
        const userData = await res.json();
        setCurrentUser(userData.username);

        // check if current user already voted
        const votedComment = commentData.comments.find(c =>
          c.voters?.includes(userData.username)
        );
        if (votedComment) {
            setVotedFor(votedComment.commenter);
        }
      }

    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCommentSubmit(e) {
    e.preventDefault();
    setCommentError('');
    setCommentSuccess('');

    try {
      const res = await fetch(`http://localhost:5000/comment/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ text: commentText })
      });

      const data = await res.json();
      if (res.ok) {
        setCommentSuccess('Comment submitted!');
        setCommentText('');
        fetchDetails();
      } else {
        setCommentError(data.error || 'Failed to submit comment');
      }
    } catch (err) {
      setCommentError(err.message);
    }
  }

  async function handleVote(candidate) {
    setVoteStatus('');
    try {
      const res = await fetch(`http://localhost:5000/vote/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ candidate })
      });
      const data = await res.json();
      if (res.ok) {
        setVoteStatus(`Voted for ${candidate}`);
        fetchDetails();
      } else {
        setVoteStatus(data.error || 'Vote failed');
      }
    } catch (err) {
      setVoteStatus(err.message);
    }
  }

  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!post) return <p>Loading post...</p>;

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
          <button type="submit">Submit</button>
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
