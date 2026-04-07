import { useState, useEffect, useCallback } from 'react';
import { fetchRankingEntries } from '../api/ranking';

export function useRanking(filters, sortBy, order, page) {
  const [entries, setEntries] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    const params = {
      ...filters,
      sort_by: sortBy,
      order: order,
      page: page,
      page_size: 20
    };

    fetchRankingEntries(params, controller.signal)
      .then(data => {
        setEntries(data.entries);
        setTotal(data.total);
        setLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      });

    return () => controller.abort();
  }, [filters, sortBy, order, page]);

  useEffect(() => {
    const cancelTimeout = refetch();
    return cancelTimeout;
  }, [refetch]);

  return { entries, total, loading, error, refetch };
}
