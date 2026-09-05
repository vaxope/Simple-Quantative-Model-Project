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

// Fetches backtest results
export async function getBacktestResults(runId) {
  const res = await fetch(`${BASE_URL}/api/backtests/${runId}/results`);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return res.json();
}

export const createBacktest = async (payload) => {
  const response = await fetch(`${BASE_URL}/api/backtests/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
  return response.json();
};

export const getBacktest = async (runId) => {
  const response = await fetch(`${BASE_URL}/api/backtests/${runId}`);
  if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
  return response.json();
};

export async function listBacktests() {
  const res = await fetch(`${BASE_URL}/api/backtests`);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return res.json();
}
