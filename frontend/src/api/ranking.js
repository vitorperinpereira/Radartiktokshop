const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchRankingEntries(params, signal) {
  const urlParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      urlParams.append(key, value);
    }
  }

  const response = await fetch(`${BASE_URL}/api/ranking/latest/entries?${urlParams.toString()}`, { signal });
  if (!response.ok) {
    throw new Error('Falha de rede ao conectar com a API de ranking');
  }
  return response.json();
}

export async function fetchRankingMeta(signal) {
  const response = await fetch(`${BASE_URL}/api/ranking/meta`, { signal });
  if (!response.ok) {
    throw new Error('Falha de rede ao carregar meta dados do ranking');
  }
  return response.json();
}

export async function fetchProduct(id, signal) {
  const response = await fetch(`${BASE_URL}/products/${id}`, { signal });
  if (!response.ok) {
    throw new Error('Falha de rede ao carregar o produto');
  }
  return response.json();
}

export async function fetchContentAngles(productId, signal) {
  const response = await fetch(`${BASE_URL}/products/${productId}/content-angles`, { signal });
  if (!response.ok) {
    throw new Error('Falha de rede ao carregar ângulos do produto');
  }
  return response.json();
}

export async function fetchProductVideos(productId, signal) {
  const response = await fetch(`${BASE_URL}/products/${productId}/videos`, { signal });
  if (!response.ok) {
    throw new Error('Falha de rede ao carregar vídeos do produto');
  }
  return response.json();
}

export async function fetchPipelineHistory(limit = 20, signal) {
  const response = await fetch(`${BASE_URL}/history/pipeline-runs?limit=${limit}`, { signal });
  if (!response.ok) {
    throw new Error('Falha ao processar histórico do pipeline na rede');
  }
  return response.json();
}

export async function fetchRankings(params = {}, signal) {
  const urlParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      urlParams.append(key, value);
    }
  }
  const response = await fetch(`${BASE_URL}/rankings?${urlParams.toString()}`, { signal });
  if (!response.ok) {
    throw new Error('Falha de rede ao carregar os rankings consolidados');
  }
  return response.json();
}
