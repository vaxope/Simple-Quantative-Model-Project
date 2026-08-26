import { useEffect, useState } from 'react';

export default function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Set how many records you want to display
  const LIMIT = 5;

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/AAPL')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        console.log("API Response Payload:", data);
        
        // Extract the array regardless of whether key is 'data', 'items', 'prices', or a direct list
        const priceList = Array.isArray(data) 
          ? data 
          : (data.items || data.data || data.prices || []);

        setPrices(priceList);
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
      
      {/* Slice the array to show only the first N items */}
      {prices.slice(0, LIMIT).map((item, index) => (
        <div key={index} style={{ marginBottom: '8px' }}>
          {/* If property keys differ, adjust date/price keys below */}
          <strong>{item.date || item.timestamp || item.created_at || index}</strong>: 
          ${item.close ?? item.price ?? item.close_price ?? JSON.stringify(item)}
        </div>
      ))}
    </div>
  );
}