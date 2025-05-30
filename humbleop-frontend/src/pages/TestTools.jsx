import { useEffect, useState } from 'react';
import { useApi } from '../hooks/useApi';

export default function TestTools() {
  const { request, loading, error } = useApi();
  const [postId, setPostId] = useState(null);
  const [log, setLog] = useState([]);
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const testUsers = ['user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user7'];
  const logStep = msg => setLog(log => [...log, msg]);

  useEffect(() => {
  const saved = localStorage.getItem('test_post_id');
  if (saved) {
    setPostId(saved);
    logStep(`🔁 Rehydrated post ID from localStorage: ${saved}`);
  }
    }, []);

useEffect(() => {
  const token = localStorage.getItem('token');
  if (!token) return;

  fetch('http://localhost:5000/profile', {
    headers: { Authorization: 'Bearer ' + token }
  })
    .then(res => res.json())
    .then(data => {
      if (data.username) setCurrentUser(data.username);
    })
    .catch(err => logStep(`❌ Failed to get profile: ${err.message}`));
    if (!postId) return;

    request(`/status/${postId}`)
        .then(p => setPost(p))
        .catch(err => logStep(`❌ Failed to load post: ${err.message}`));

    request(`/comments/${postId}`)
        .then(res => setComments(res.comments || []))
        .catch(err => logStep(`❌ Failed to load comments: ${err.message}`));
    }, [postId, request]);


    async function loginAs(username) {
    try {
        const res = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password: 'user' }) // stessa password per tutti
        });
        const data = await res.json();
        if (res.ok && data.access_token) {
        localStorage.setItem('token', data.access_token);

        // ✅ Salva anche l'ID del post corrente prima del reload
        if (postId) {
            localStorage.setItem('test_post_id', postId);
        }

        logStep(`🔐 Logged in as ${username}`);
        window.location.reload(); // ricarica la pagina con il nuovo utente
        } else {
        logStep(`❌ Login failed for ${username}`);
        }
    } catch (err) {
        logStep(`❌ Login error: ${err.message}`);
    }
    }

  async function createTestPost() {
    try {
      const generatedId = Math.random().toString(36).slice(2);
      await request(`/create_post/${generatedId}`, 'POST', {
        body: '🔥 Test post generated from /test page',
        voting_ends_in: 15
      });

      setPostId(generatedId);
      logStep(`✅ Post created: ID ${generatedId}`);
    } catch (err) {
      logStep(`❌ Failed to create post: ${err.message}`);
    }
  }

    async function addComment() {
    if (!postId) return logStep('⚠️ No post ID set yet');
    try {
        await request(`/comment/${postId}`, 'POST', {
        text: `Test comment from ${currentUser}`
        });
        logStep(`✅ Comment added by ${currentUser}`);

        // 👇 ricarica subito la lista commenti dopo il successo
        const data = await request(`/comments/${postId}`);
        setComments(data.comments || []);

    } catch (err) {
        logStep(`❌ Failed to add comment: ${err.message}`);
    }
    }

    async function voteForSelected() {
    if (!postId) return logStep('⚠️ No post ID set yet');
    if (!selectedCandidate) return logStep('⚠️ No candidate selected');
    if (selectedCandidate === currentUser) return logStep('⛔ Cannot vote for yourself');

    try {
        await request(`/vote/${postId}`, 'POST', { candidate: selectedCandidate });
        logStep(`🗳️ Voted for ${selectedCandidate}`);

        // aggiorna i commenti con i nuovi voti
        const data = await request(`/comments/${postId}`);
        setComments(data.comments || []);
    } catch (err) {
        logStep(`❌ Vote failed: ${err.message}`);
    }
    }

  async function forceEnd() {
    if (!postId) return logStep('⚠️ No post ID set yet');
    try {
      await request(`/debug/expire_post/${postId}`, 'POST');
      logStep('⏳ Forced post expiration');
    } catch (err) {
      logStep(`❌ Failed to force expiration: ${err.message}`);
    }
  }

    function resetTest() {
    localStorage.removeItem('token');
    localStorage.removeItem('test_post_id');
    setPostId(null);
    setPost(null);
    setComments([]);
    setLog([]);
    setCurrentUser(null);
    logStep('🧹 Test reset. Reloading...');
    setTimeout(() => window.location.reload(), 500);
    }

async function runFullDuelTest() {
  try {
    logStep('🚀 Running full duel test...');

    const users = ['user1', 'user2', 'user3', 'user4'];
    const delay = ms => new Promise(res => setTimeout(res, ms));
    let token = null;

    // STEP 1: user1 creates post
    token = await loginSilent(users[0]);
    const generatedId = Math.random().toString(36).slice(2);
    await fetch(`http://localhost:5000/create_post/${generatedId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token
      },
      body: JSON.stringify({
        body: '🧪 Duel test post',
        voting_ends_in: 15
      })
    });
    localStorage.setItem('test_post_id', generatedId);
    setPostId(generatedId);
    logStep(`✅ Post created: ${generatedId}`);
    await delay(400);

    // STEP 2: user2 comments
    token = await loginSilent(users[1]);
    await fetch(`http://localhost:5000/comment/${generatedId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token
      },
      body: JSON.stringify({ text: `Comment from ${users[1]}` })
    });
    logStep(`💬 ${users[1]} commented`);
    await delay(400);

    // STEP 3: user3 comments
    token = await loginSilent(users[2]);
    await fetch(`http://localhost:5000/comment/${generatedId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token
      },
      body: JSON.stringify({ text: `Comment from ${users[2]}` })
    });
    logStep(`💬 ${users[2]} commented`);
    await delay(400);

    // STEP 4: user4 votes for user2
    token = await loginSilent(users[3]);
    await fetch(`http://localhost:5000/vote/${generatedId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token
      },
      body: JSON.stringify({ candidate: users[1] })
    });
    logStep(`🗳️ ${users[3]} voted for ${users[1]}`);
    await delay(400);

    // STEP 5: user1 ends the post
    token = await loginSilent(users[0]);
    await fetch(`http://localhost:5000/debug/expire_post/${generatedId}`, {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + token
      }
    });
    logStep(`⏳ Post forcibly expired`);

    // STEP 6: redirect to victory page
    window.location.href = `/victory/${generatedId}`;
  } catch (err) {
    logStep(`❌ Test failed: ${err.message}`);
  }
}

async function loginSilent(username) {
  const res = await fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password: 'user' })
  });
  const data = await res.json();
  if (res.ok && data.access_token) {
    localStorage.setItem('token', data.access_token);
    logStep(`🔐 Switched to ${username}`);
    return data.access_token;
  } else {
    throw new Error(`Login failed for ${username}`);
  }
}


  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">🧪 Test Tools</h1>

      <div className="mb-4">
        <label className="block font-semibold mb-1">Login as test user:</label>
        <select onChange={(e) => loginAs(e.target.value)} className="border px-2 py-1 rounded">
          <option value="">-- Select user --</option>
          {testUsers.map(u => (
            <option key={u} value={u}>{u}</option>
          ))}
        </select>
      </div>

      {currentUser && (
        <p className="text-sm text-gray-700 mb-4">
            👤 Logged in as: <strong>{currentUser}</strong>
        </p>
        )}

      <div className="space-y-2">
        <button onClick={createTestPost} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded">Create Post</button>
        <button onClick={addComment} disabled={loading || !postId} className="bg-green-600 text-white px-4 py-2 rounded">Add Comment</button>
        <button onClick={voteForSelected} disabled={loading || !postId || !selectedCandidate} className="bg-blue-500 text-white px-4 py-2 rounded mt-2">Confirm vote</button>
        <button onClick={forceEnd} disabled={loading} className="bg-red-600 text-white px-4 py-2 rounded">Force End Post</button>
        <button onClick={runFullDuelTest} className="bg-indigo-600 text-white px-4 py-2 rounded">🧪 Run Full Duel Test</button>
        <button onClick={resetTest} className="bg-gray-600 text-white px-4 py-2 rounded">  🧹 Reset Test</button>
      </div>
          {post && (
  <div className="border p-3 rounded bg-white shadow mt-6">
    <p className="text-sm text-gray-500">Author: {post.author}</p>
    <p className="font-medium">{post.body}</p>
  </div>
    )}

    {comments.length > 0 ? (
    <ul className="mt-2 space-y-1 text-sm">
      {comments.map((c) => (
        <li key={`${c.commenter}-${c.text}`}>
          <strong>{c.commenter}</strong>: {c.text} ({c.votes} votes)
        </li>
      ))}
    </ul>
    ) : (
    <p className="text-sm text-gray-500 mt-2">No comments yet.</p>
    )}
        {comments.length > 0 && (
    <div className="mt-4">
        <label className="block mb-1 font-semibold">Vote for:</label>
        <select
        value={selectedCandidate}
        onChange={(e) => setSelectedCandidate(e.target.value)}
        className="border px-2 py-1 rounded"
        >
        <option value="">-- Select a comment author --</option>
        {comments.map((c) => (
          <option key={c.commenter} value={c.commenter}>
            {c.commenter}
          </option>
        ))}
        </select>
    </div>
    )}

      <div className="mt-6">
        <h2 className="font-bold mb-2">Log</h2>
        <ul className="text-sm text-gray-800 space-y-1">
          {log.map((line, i) => (
            <li key={i}>• {line}</li>
          ))}
        </ul>
      </div>

      {error && <p className="text-red-600 mt-2">{error}</p>}
    </div>
  );
}
