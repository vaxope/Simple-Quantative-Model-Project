import { useEffect, useState } from 'react';
import { getPrices } from '../client';

// Fetches and isplays a sliced list of historical prices for a specific ticker 
export default function Pricelist({ ticker, limit = 5, start = '2024-01-01' }) {
  // State management for raw price data, loading status, and error handling
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!ticker) return;

    setLoading(true);
    // Fetches prices history from backend
    getPrices(ticker, { start })
      .then((data) => {
        setPrices(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [ticker, start]);

  // Conditional UI state based on API response
  if (loading) return <div>Loading prices...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ marginBottom: '24px' }}>
      <h3>{ticker} — First {Math.min(limit, prices.length)} Prices</h3>
      {prices.slice(0, limit).map((item) => (
        <div key={item.date} style={{ marginBottom: '4px' }}>
          <strong>{item.date}</strong>: ${item.close.toFixed(2)}
        </div>
      ))}
    </div>
  );
}