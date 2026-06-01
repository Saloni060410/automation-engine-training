import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.engine import parse_command
from engine.executor import execute_workflow

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    command: str


@app.get('/')
def health_check():
    return {'status': 'ok'}


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'components': ['email_reader', 'pdf_parser', 'llm_extractor', 'validator', 'api_caller']
    }


@app.post('/run-workflow')
def run_workflow(request: WorkflowRequest):
    try:
        workflow = parse_command(request.command)
        result = execute_workflow(workflow)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
