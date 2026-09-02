import { useEffect, useState } from 'react'
import { getLatestSignals } from '../client'

// Fetches and renders latest signals from API
export default function SignalList() {
    // State management for signals, loading status, and API errors
    const [signals, setSignals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      // Fetch latest signal predictions
        getLatestSignals()
        .then((data) => {
            setSignals(data);
            setLoading(false);
        })
        .catch((err) => {
            setError(err.message);
            setLoading(false);
        });
    }, []);

    // Conditional UI rendering
    if (loading) return <div>Loading signals...</div>;
    if (error) return <div>Error loading signals: {error}</div>;

  return (
    <div>
      <h3>Latest Trading Signals</h3>
      {signals.map((item) => (
        <div key={item.ticker} style={{ marginBottom: '4px' }}>
          <strong>{item.ticker}</strong> ({item.date}): {item.signal} (Score: {item.score ?? 'N/A'})
        </div>
      ))}
    </div>
  );
}