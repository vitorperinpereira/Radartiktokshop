import { useState, useEffect } from 'react';
import { fetchPipelineHistory } from '../api/ranking';

export function usePipelineHistory(limit = 20) {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const controller = new AbortController();
    fetchPipelineHistory(limit, controller.signal)
      .then(data => {
        setRuns(data.items || []);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      });

    return () => controller.abort();
  }, [limit]);

  return { runs, loading, error };
}
