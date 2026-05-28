function ExecutionStatus({ log }) {
  const statusColor = {
    success: '#059669',
    error: '#e53e3e',
    running: '#d97706',
  };

  const overallColor = log.status === 'completed' ? '#059669'
    : log.status === 'partial' ? '#d97706' : '#e53e3e';

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>
        Execution Log —{' '}
        <span style={{ color: overallColor }}>{log.status.toUpperCase()}</span>
      </h2>
      <div style={styles.steps}>
        {log.steps.map((step, i) => (
          <div key={i} style={styles.card}>
            <div style={styles.header}>
              <span style={styles.stepLabel}>Step {step.step} — {step.component}</span>
              <span style={{ color: statusColor[step.status] || '#666', fontWeight: '700' }}>
                {step.status}
              </span>
            </div>
            <div style={styles.meta}>Duration: {step.duration_seconds}s</div>
            {step.input_params && Object.keys(step.input_params).length > 0 && (
              <div style={styles.section}>
                <span style={styles.label}>Input: </span>
                <code style={styles.code}>{JSON.stringify(step.input_params)}</code>
              </div>
            )}
            <div style={styles.section}>
              <span style={styles.label}>Output: </span>
              <pre style={styles.output}>
                {typeof step.output_summary === 'string'
                  ? step.output_summary
                  : JSON.stringify(step.output_summary, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: { padding: '20px 40px' },
  heading: { fontSize: '20px', marginBottom: '20px', color: '#1a1a2e' },
  steps: { display: 'flex', flexDirection: 'column', gap: '16px' },
  card: {
    background: '#fff', border: '1px solid #e2e8f0', borderRadius: '10px',
    padding: '16px 20px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
  },
  header: { display: 'flex', justifyContent: 'space-between', marginBottom: '6px' },
  stepLabel: { fontWeight: '600', color: '#1a1a2e', fontSize: '15px' },
  meta: { fontSize: '12px', color: '#888', marginBottom: '8px' },
  section: { marginTop: '6px' },
  label: { fontSize: '12px', fontWeight: '600', color: '#555' },
  code: { fontSize: '12px', color: '#444', background: '#f5f5ff', padding: '2px 6px', borderRadius: '4px' },
  output: {
    fontSize: '12px', background: '#f8fafc', border: '1px solid #e2e8f0',
    borderRadius: '6px', padding: '8px', marginTop: '4px',
    maxHeight: '150px', overflowY: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-word',
  },
};

export default ExecutionStatus;
