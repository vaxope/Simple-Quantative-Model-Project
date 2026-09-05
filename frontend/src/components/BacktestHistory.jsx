import { useEffect, useState } from 'react';
import { listBacktests } from '../api/client';

export default function BacktestHistory({ selectedRunId, onSelectRun, refreshTrigger }) {
    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState([]);

    const fetchHistory = () => {
        setLoading(true);
        listBacktests()
            .then((data) => {
                setRuns(data);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }

    useEffect(() => {
        fetchHistory();
    }, [refreshTrigger]);

    if (loading) return <div>Loading history...</div>

return (
    <div style={{ border: '1px solid #ccc', padding: '16px', borderRadius: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>Past Backtests</h3>
        <button onClick={fetchHistory}>Refresh</button>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ddd' }}>
            <th>ID</th>
            <th>Name</th>
            <th>Model</th>
            <th>Status</th>
            <th>Sharpe</th>
            <th>Max DD</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => (
            <tr
              key={r.id}
              style={{
                borderBottom: '1px solid #eee',
                backgroundColor: selectedRunId === r.id ? '#f0f7ff' : 'transparent',
              }}
            >
              <td>{r.id}</td>
              <td>{r.run_name}</td>
              <td>{r.model_name}</td>
              <td>{r.status}</td>
              <td>{r.sharpe != null ? r.sharpe.toFixed(2) : '-'}</td>
              <td>{r.max_drawdown != null ? `${(r.max_drawdown * 100).toFixed(1)}%` : '-'}</td>
              <td>
                <button
                  disabled={r.status !== 'completed'}
                  onClick={() => onSelectRun(r.id)}
                >
                  {selectedRunId === r.id ? 'Viewing' : 'View Curve'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}