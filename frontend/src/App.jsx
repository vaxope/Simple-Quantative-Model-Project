import { useEffect, useState } from 'react';

export default function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Set how many records you want to display
  const LIMIT = 5;

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/prices/AAPL?start=2024-01-01')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setPrices(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading prices...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Showing First {Math.min(LIMIT, prices.length)} Prices</h2>
      
      {prices.slice(0, LIMIT).map((item) => (
        <div key={item.date} style={{ marginBottom: '8px' }}>
          <strong>{item.date}</strong>: ${item.close.toFixed(2)}
        </div>
      ))}
    </div>
  );
}