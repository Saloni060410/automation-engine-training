import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from engine.engine import parse_command
from engine.executor import execute_workflow

app = FastAPI()


class WorkflowRequest(BaseModel):
    command: str


@app.get('/')
def health_check():
    return {'status': 'ok'}


@app.post('/run-workflow')
def run_workflow(request: WorkflowRequest):
    try:
        workflow = parse_command(request.command)
        result = execute_workflow(workflow)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
