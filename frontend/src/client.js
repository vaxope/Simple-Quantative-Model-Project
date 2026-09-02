const BASE_URL = 'http://127.0.0.1:8000';

// Fetches historical price data for a given ticker
export async function getPrices(ticker, { start, end } = {}) {
  const params = new URLSearchParams();
  if (start) params.set('start', start);
  if (end) params.set('end', end);
  const res = await fetch(`${BASE_URL}/api/prices/${ticker}?${params}`);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return res.json();
}

// Fetches latest trading signals across all tickers
export async function getLatestSignals() {
  const res = await fetch(`${BASE_URL}/api/signals/latest`);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return res.json();
}

// Fetches trading signal for a given ticker
export async function getSignal(ticker, {start, end} = {}) {
  const params = new URLSearchParams();
  if (start) params.set('start', start);
  if (end) params.set('end', end);
  const res = await fetch(`${BASE_URL}/api/signals/${ticker}?${params}`);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return res.json();
}
