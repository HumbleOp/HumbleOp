import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { v4 as uuidv4 } from 'uuid';
import { toast } from 'react-hot-toast';

export default function CreatePost() {
  const [body, setBody] = useState('');
  const [votingHours, setVotingHours] = useState(24);
  const navigate = useNavigate();
  const { token } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    const postId = uuidv4().slice(0, 8);

    try {
      const res = await fetch(`http://localhost:5000/create_post/${postId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({
          body,
          voting_hours: votingHours
        })
      });
      const data = await res.json();
      if (res.ok) {
        toast.success('Post created!');
        setBody('');
        setVotingHours(24);
        setTimeout(() => navigate('/profile'), 1500);
      } else {
        toast.error(data.error || 'Error');
      }
    } catch (err) {
      toast.error(err.message || 'Something went wrong');
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Create a new post</h2>
      <textarea
        placeholder="What's on your mind?... Use #tag to add a tag."
        value={body}
        onChange={e => setBody(e.target.value)}
        rows={6}
        style={{ width: '100%' }}
      />
      <div>
        <label>Voting time window: </label>
        <input
          type="number"
          min="1"
          value={votingHours}
          onChange={e => setVotingHours(parseFloat(e.target.value))}
        />
      </div>
      <button type="submit">Pubblica</button>
    </form>
  );
}
