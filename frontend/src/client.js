const BASE_URL = 'http://127.0.0.1:8000';

export async function getPrices(ticker, { start, end } = {}) {
  const params = new URLSearchParams();
  if (start) params.set('start', start);
  if (end) params.set('end', end);
  const res = await fetch(`${BASE_URL}/api/prices/${ticker}?${params}`);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return res.json();
}

export async function getLatestSignals() {
  
}

export async function getSignal(ticker, {start, end}) {
    
}