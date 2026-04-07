import { useState } from 'react';

export function useFilters() {
  const [filters, setFiltersState] = useState({ category: '', label: '', min_score: 0, classification: '' });
  const [sortBy, setSortByState] = useState('final_score');
  const [order, setOrderState] = useState('desc');
  const [page, setPageState] = useState(1);

  const resetPage = () => setPageState(1);

  const setFilters = (newFilters) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }));
    resetPage();
  };

  const setSortBy = (newSort) => {
    setSortByState(newSort);
    resetPage();
  };

  const setOrder = (newOrder) => {
    setOrderState(newOrder);
    resetPage();
  };
  
  const setPage = (newPage) => {
    setPageState(newPage);
  };

  const resetFilters = () => {
    setFiltersState({ category: '', label: '', min_score: 0, classification: '' });
    setSortByState('final_score');
    setOrderState('desc');
    resetPage();
  };

  return {
    filters,
    sortBy,
    order,
    page,
    setFilters,
    setSortBy,
    setOrder,
    setPage,
    resetFilters
  };
}
