const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchGarageItems(signal) {
  const response = await fetch(`${BASE_URL}/api/garage`, { signal });
  if (!response.ok) {
    throw new Error('Falha ao carregar a garagem');
  }
  return response.json();
}

export async function addGarageItem(productId) {
  const response = await fetch(`${BASE_URL}/api/garage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId })
  });
  if (!response.ok) {
    throw new Error('Falha ao adicionar produto à garagem');
  }
  return response.json();
}

export async function updateGarageItemStatus(productId, status) {
  const response = await fetch(`${BASE_URL}/api/garage/${productId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  if (!response.ok) {
    throw new Error('Falha ao atualizar status do produto');
  }
  return response.json();
}

export async function removeGarageItem(productId) {
  const response = await fetch(`${BASE_URL}/api/garage/${productId}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    throw new Error('Falha ao remover produto da garagem');
  }
}
