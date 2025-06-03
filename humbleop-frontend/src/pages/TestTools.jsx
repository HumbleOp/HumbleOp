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
        body: JSON.stringify({ username, password: 'user' })
      });
      const data = await res.json();
      if (res.ok && data.access_token) {
        localStorage.setItem('token', data.access_token);
        if (postId) {
          localStorage.setItem('test_post_id', postId);
        }
        logStep(`🔐 Logged in as ${username}`);
        window.location.reload();
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
      voting_hours: 15   // <-- CORRETTO: deve chiamarsi voting_hours
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

  async function markDuelStarted() {
    if (!postId) return logStep('⚠️ No post ID set yet');
    try {
      await request(`/start_now/${postId}`, 'POST');
      logStep('🔥 Post marked as duel started');
    } catch (err) {
      logStep(`❌ Failed to mark duel started: ${err.message}`);
    }
  }

  async function startFullDuel() {
    if (!postId) return logStep('⚠️ No post ID set yet');
    try {
      await request(`/start_duel/${postId}`, 'POST');
      logStep('🥊 Duel officially started via /start_duel');
    } catch (err) {
      logStep(`❌ Failed to start full duel: ${err.message}`);
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
        <p className="text-sm text-gray-700 mb-2">
          👤 Logged in as: <strong>{currentUser}</strong>
        </p>
      )}

      {postId && (
        <div className="mb-4 space-y-1">
          <p className="text-sm text-gray-500">
            📌 Current Post ID: <code className="bg-gray-800 text-white px-2 py-1 rounded">{postId}</code>
          </p>
          <a
            href={`/duel/${postId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-purple-700 text-white px-4 py-1 rounded hover:bg-purple-600 text-sm"
          >
            ⚔️ Open Duel Page
          </a>
        </div>
      )}

      <div className="space-y-2">
        <button onClick={createTestPost} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded">Create Post</button>
        <button onClick={addComment} disabled={loading || !postId} className="bg-green-600 text-white px-4 py-2 rounded">Add Comment</button>
        <button onClick={voteForSelected} disabled={loading || !postId || !selectedCandidate} className="bg-blue-500 text-white px-4 py-2 rounded mt-2">Confirm vote</button>
        <button onClick={forceEnd} disabled={loading} className="bg-red-600 text-white px-4 py-2 rounded">Force End Post</button>
        <button onClick={markDuelStarted} disabled={loading} className="bg-yellow-500 text-black px-4 py-2 rounded">🔥 Start Duel Now</button>
        <button onClick={startFullDuel} disabled={loading} className="bg-orange-600 text-white px-4 py-2 rounded">🥊 Start Duel (Full)</button>
        <button onClick={resetTest} className="bg-gray-600 text-white px-4 py-2 rounded">🧹 Reset Test</button>
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
