import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useCallback } from 'react';

export function useApi() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

const request = useCallback(async (endpoint, method = 'GET', body = null, retries = 1) => {
  setLoading(true);
  setError(null);
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: 'Bearer ' + token })
  };

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(`http://localhost:5000${endpoint}`, {
        method,
        headers,
        ...(body && { body: JSON.stringify(body) })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Request failed');

      setLoading(false);
      return data;

    } catch (err) {
      if (attempt === retries) {
        setError(err.message);
        setLoading(false);
        throw err;
      }
      await new Promise(res => setTimeout(res, 500));
    }
  }
}, [token]);

  return { request, loading, error };
}
