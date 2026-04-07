import { useState, useEffect } from 'react';
import { fetchContentAngles } from '../api/ranking';

export function useContentAngles(productId) {
  const [angles, setAngles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!productId) {
      setAngles([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    const controller = new AbortController();
    fetchContentAngles(productId, controller.signal)
      .then(data => {
        setAngles(data.angles || []);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      });

    return () => controller.abort();
  }, [productId]);

  return { angles, loading, error };
}
