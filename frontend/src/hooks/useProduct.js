import { useState, useEffect } from 'react';
import { fetchProduct } from '../api/ranking';

export function useProduct(id) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    const controller = new AbortController();
    fetchProduct(id, controller.signal)
      .then(data => {
        setProduct(data);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      });

    return () => controller.abort();
  }, [id]);

  return { product, loading, error };
}
