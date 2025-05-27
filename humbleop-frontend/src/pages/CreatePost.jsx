import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { v4 as uuidv4 } from 'uuid';

export default function CreatePost() {
  const [body, setBody] = useState('');
  const [votingHours, setVotingHours] = useState(24);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();
  const { token } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
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
        setSuccess('Post creato con successo!');
        setBody('');
        setVotingHours(24);
        setTimeout(() => navigate('/profile'), 1500);
      } else {
        setError(data.error || 'Errore');
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Crea un nuovo post</h2>
      <textarea
        placeholder="Scrivi il tuo post... Usa #tag per aggiungere tag."
        value={body}
        onChange={e => setBody(e.target.value)}
        rows={6}
        style={{ width: '100%' }}
      />
      <div>
        <label>Ore di voto: </label>
        <input
          type="number"
          min="1"
          value={votingHours}
          onChange={e => setVotingHours(parseFloat(e.target.value))}
        />
      </div>
      <button type="submit">Pubblica</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
    </form>
  );
}
