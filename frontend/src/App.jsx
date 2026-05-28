import { useState } from 'react';
import CommandInput from './components/CommandInput';
import WorkflowCanvas from './components/WorkflowCanvas';
import ExecutionStatus from './components/ExecutionStatus';

function App() {
  const [workflow, setWorkflow] = useState(null);
  const [executionLog, setExecutionLog] = useState(null);
  const [executing, setExecuting] = useState(false);

  function handleWorkflowReady(data) {
    setWorkflow(data);
    setExecutionLog(null);
  }

  async function handleExecute() {
    if (!workflow) return;
    setExecuting(true);
    setExecutionLog(null);
    try {
      // The API already runs the workflow and returns the log in one call.
      // We reuse the data already returned from CommandInput's POST call.
      setExecutionLog(workflow);
    } finally {
      setExecuting(false);
    }
  }

  return (
    <div style={styles.page}>
      <CommandInput onWorkflowReady={handleWorkflowReady} />

      {workflow && (
        <WorkflowCanvas
          steps={workflow.steps}
          onExecute={handleExecute}
          executing={executing}
        />
      )}

      {executionLog && <ExecutionStatus log={executionLog} />}
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh',
    background: '#f0f4ff',
    fontFamily: 'Inter, system-ui, sans-serif',
    paddingBottom: '60px',
  },
};

export default App;
