function WorkflowCanvas({ steps, onExecute, executing }) {
  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Workflow Plan</h2>
      <div style={styles.canvas}>
        {steps.map((step, i) => (
          <div key={i} style={styles.nodeWrapper}>
            <div style={styles.card}>
              <div style={styles.stepBadge}>Step {step.step}</div>
              <div style={styles.component}>{step.component}</div>
              {Object.keys(step.params || {}).length > 0 && (
                <pre style={styles.params}>{JSON.stringify(step.params, null, 2)}</pre>
              )}
            </div>
            {i < steps.length - 1 && <div style={styles.arrow}>→</div>}
          </div>
        ))}
      </div>
      <button style={styles.button} onClick={onExecute} disabled={executing}>
        {executing ? 'Executing...' : 'Execute Workflow'}
      </button>
    </div>
  );
}

const styles = {
  container: { padding: '20px', textAlign: 'center' },
  heading: { fontSize: '20px', marginBottom: '20px', color: '#1a1a2e' },
  canvas: { display: 'flex', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap', gap: '8px' },
  nodeWrapper: { display: 'flex', alignItems: 'center', gap: '8px' },
  card: {
    background: '#fff', border: '1.5px solid #4f46e5', borderRadius: '10px',
    padding: '14px 18px', minWidth: '130px', boxShadow: '0 2px 8px rgba(79,70,229,0.1)',
  },
  stepBadge: {
    fontSize: '11px', fontWeight: '700', color: '#4f46e5',
    textTransform: 'uppercase', marginBottom: '6px',
  },
  component: { fontSize: '15px', fontWeight: '600', color: '#1a1a2e' },
  params: {
    fontSize: '11px', color: '#666', marginTop: '6px',
    textAlign: 'left', background: '#f5f5ff', borderRadius: '4px', padding: '6px',
  },
  arrow: { fontSize: '22px', color: '#4f46e5', fontWeight: 'bold' },
  button: {
    marginTop: '28px', padding: '10px 28px', fontSize: '15px',
    backgroundColor: '#059669', color: '#fff', border: 'none',
    borderRadius: '8px', cursor: 'pointer',
  },
};

export default WorkflowCanvas;
