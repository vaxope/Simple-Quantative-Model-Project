import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { getBacktestResults } from '../api/client';

function computeCumulativeReturns(results) {
  if (!results || results.length === 0) return [];

  const returnsByDate = new Map();

  for (const row of results) {
    if (!returnsByDate.has(row.date)) {
      returnsByDate.set(row.date, []);
    }
    returnsByDate.get(row.date).push(row.net_return ?? 0);
  }

  const sortedDates = Array.from(returnsByDate.keys()).sort();

  let cumulative = 1;
  return sortedDates.map((date) => {
    const dailyReturns = returnsByDate.get(date);
    const avgDailyReturn =
      dailyReturns.reduce((sum, val) => sum + val, 0) / dailyReturns.length;

    cumulative *= (1 + avgDailyReturn);

    return {
      date,
      cumulative_return: Number(cumulative.toFixed(4)),
    };
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