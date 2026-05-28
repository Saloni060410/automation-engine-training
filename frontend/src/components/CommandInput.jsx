import { useState } from 'react';
import axios from 'axios';

function CommandInput({ onWorkflowReady }) {
  const [command, setCommand] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!command.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await axios.post('http://localhost:8000/run-workflow', { command });
      onWorkflowReady(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Automation Engine</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          style={styles.input}
          type="text"
          placeholder="Enter a command (e.g. read email, enter invoice to SAP)"
          value={command}
          onChange={e => setCommand(e.target.value)}
        />
        <button style={styles.button} type="submit" disabled={loading}>
          {loading ? 'Running...' : 'Run'}
        </button>
      </form>
      {error && <p style={styles.error}>{error}</p>}
    </div>
  );
}

const styles = {
  container: { textAlign: 'center', padding: '40px 20px' },
  title: { fontSize: '28px', marginBottom: '24px', color: '#1a1a2e' },
  form: { display: 'flex', justifyContent: 'center', gap: '10px' },
  input: {
    width: '400px', padding: '10px 14px', fontSize: '15px',
    border: '1.5px solid #ccc', borderRadius: '8px', outline: 'none',
  },
  button: {
    padding: '10px 24px', fontSize: '15px', backgroundColor: '#4f46e5',
    color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer',
  },
  error: { color: '#e53e3e', marginTop: '12px' },
};

export default CommandInput;
