import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { getBacktestResults } from '../api/client';

function computeCumulativeReturns(results) {
  let cumulative = 1;
  return results.map((row) => {
    cumulative *= (1 + (row.net_return ?? 0));
    return { date: row.date, cumulative_return: cumulative };
  });
}

export default function EquityCurve({ runId }) {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!runId) return;

    setLoading(true);
    getBacktestResults(runId)
      .then((data) => {
        setChartData(computeCumulativeReturns(data));
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [runId]);

  if (loading) return <div>Loading equity curve...</div>;
  if (error) return <div>Error loading chart: {error}</div>;

  return (
    <LineChart width={600} height={300} data={chartData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="cumulative_return" dot={false} />
    </LineChart>
  );
}