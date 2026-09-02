import PriceList from './components/PriceList';
import SignalList from './components/SignalList';

export default function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Trading Dashboard</h2>
      
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