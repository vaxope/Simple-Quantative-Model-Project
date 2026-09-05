import { useState } from 'react';
import PriceList from './components/PriceList';
import SignalList from './components/SignalList';
import BacktestTrigger from './components/BacktestTrigger';
import BacktestHistory from './components/BacktestHistory';
import EquityCurve from './components/EquityCurve';

export default function App() {
  const [selectedRunId, setSelectedRunId] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);

  const handleRunCompleted = (runId) => {
    setSelectedRunId(runId);
    setRefreshCount((prev) => prev + 1);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Trading Dashboard</h2>

      <section style={{ marginBottom: '24px' }}>
        <BacktestTrigger onRunCompleted={handleRunCompleted} />
      </section>

      <section style={{ marginBottom: '24px' }}>
        <BacktestHistory
          selectedRunId={selectedRunId}
          onSelectRun={(id) => setSelectedRunId(id)}
          refreshTrigger={refreshCount}
        />
      </section>

      {selectedRunId && (
        <section style={{ marginBottom: '32px' }}>
          <h3>Equity Curve (Run #{selectedRunId})</h3>
          <EquityCurve runId={selectedRunId} />
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