import { useState, useEffect } from 'react'; 
import { createBacktest, getBacktest } from '../api/client';

export default function BacktestTrigger({ onRunCompleted }) {
    const [tickersInput, setTickersInput] = useState('AAPL, MSFT, NVDA');
    const [modelName, setModelName] = useState('xgb');
    const [costBps, setCostBps] = useState(5);
    const [activeRunId, setActiveRunId] = useState(null);
    const [status, setStatus] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg(null);
        setStatus('submitting');

        const tickers = tickersInput
            .split(',')
            .map((t) => t.trim().toUpperCase())
            .filter(Boolean);

        try {
            const data = await createBacktest({
                run_name: `run_${Date.now()}`,
                tickers,
                model_name: modelName,
                cost_bps: Number(costBps)
            });

            setActiveRunId(data.id);
            setStatus('running');
        } catch (err) {
            setErrorMsg(err.message);
            setStatus('failed');
        }
    };

    useEffect(() => {
        if (!activeRunId || status !== 'running') return;

        const interval = setInterval(async () => {
            try {
                const run = await getBacktest(activeRunId);
                if (run.status === 'completed') {
                    setStatus('completed');
                    clearInterval(interval);
                    onRunCompleted(activeRunId);
                } else if (run.status === 'failed') {
                    setStatus('failed');
                    setErrorMsg(run.error_message || 'Backtest failed');
                    clearInterval(interval);
                }
            } catch (err) {
                setErrorMsg(err.message);
                setStatus('failed');
                clearInterval(interval);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [activeRunId, status, onRunCompleted]);
    
    return (
      <div style={{ border: '1px solid #ccc', padding: '16px', borderRadius: '8px' }}>
        <h3>Run New Backtest</h3>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={tickersInput}
            onChange={(e) => setTickersInput(e.target.value)}
            placeholder="AAPL, MSFT, NVDA"
            disabled={status === 'running'}
          />
          <button type="submit" disabled={status === 'running'}>
            {status === 'running' ? 'Running...' : 'Start Backtest'}
          </button>
        </form>
        {status && <p>Status: <strong>{status}</strong> {activeRunId && `(ID: ${activeRunId})`}</p>}
        {errorMsg && <p style={{ color: 'red' }}>{errorMsg}</p>}
      </div>
    );
}