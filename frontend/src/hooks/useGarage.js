import { useState, useEffect, useCallback } from 'react';
import { fetchGarageItems, addGarageItem, updateGarageItemStatus, removeGarageItem } from '../api/garage';

export function useGarage() {
  const [savedProducts, setSavedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadGarage = useCallback(async () => {
    const controller = new AbortController();
    try {
      setLoading(true);
      const items = await fetchGarageItems(controller.signal);
      setSavedProducts(items);
      setError(null);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGarage();
  }, [loadGarage]);

  const saveProduct = async (product) => {
    const productId = product.product_id || product.id;
    try {
      const newItem = await addGarageItem(productId);
      setSavedProducts(prev => {
        if (prev.find(p => p.product_id === newItem.product_id)) return prev;
        return [newItem, ...prev];
      });
    } catch (err) {
      console.error(err);
    }
  };

  const removeProduct = async (id) => {
    try {
      await removeGarageItem(id);
      setSavedProducts(prev => prev.filter(p => p.product_id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const updateStatus = async (id, status) => {
    try {
      const updatedItem = await updateGarageItemStatus(id, status);
      setSavedProducts(prev => prev.map(p => p.product_id === id ? updatedItem : p));
    } catch (err) {
      console.error(err);
    }
  };

  const isSaved = (id) => savedProducts.some(p => p.product_id === id);

  return { savedProducts, saveProduct, removeProduct, updateStatus, isSaved, loading, error };
}
