import { useState } from 'react';
import PriceList from './components/PriceList';
import SignalList from './components/SignalList';
import BacktestTrigger from './components/BacktestTrigger';
import EquityCurve from './components/EquityCurve';

export default function App() {
  const [completedRunId, setCompletedRunId] = useState(null);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Trading Dashboard</h2>

      <section style={{ marginBottom: '32px' }}>
        <BacktestTrigger onRunCompleted={(id) => setCompletedRunId(id)} />
      </section>

      {completedRunId && (
        <section style={{ marginBottom: '32px' }}>
          <h3>Equity Curve (Run #{completedRunId})</h3>
          <EquityCurve runId={completedRunId} />
        </section>
      )}

      <section style={{ marginBottom: '32px' }}>
        <PriceList ticker="AAPL" limit={5} start="2024-01-01" />
        <PriceList ticker="MSFT" limit={5} start="2024-01-01" />
      </section>

      <section>
        <SignalList />
      </section>
    </div>
  );
}