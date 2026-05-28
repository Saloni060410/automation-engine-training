# Workflow Schema

Each workflow is a JSON array of steps. Every step follows this structure:

```json
{
  "step": 1,
  "component": "email_reader",
  "params": {}
}
```

## Fields

| Field | Type | Description |
|---|---|---|
| `step` | integer | Step number, starting from 1 |
| `component` | string | Which component to run (see available components below) |
| `params` | object | Input parameters passed to the component |

## Available Components

| Component | What it does |
|---|---|
| `email_reader` | Reads and fetches emails from a mailbox |
| `pdf_parser` | Extracts raw text from PDF files |
| `llm_extractor` | Uses an LLM to extract structured data from text |
| `validator` | Validates invoice data against business rules |
| `api_caller` | Sends data to an external API (e.g. SAP) |

## Examples

### "read email"

```json
[
  {
    "step": 1,
    "component": "email_reader",
    "params": { "folder": "inbox" }
  }
]
```

### "compare excel files"

```json
[
  {
    "step": 1,
    "component": "pdf_parser",
    "params": { "file": "file1.xlsx" }
  },
  {
    "step": 2,
    "component": "pdf_parser",
    "params": { "file": "file2.xlsx" }
  },
  {
    "step": 3,
    "component": "llm_extractor",
    "params": { "task": "compare the two files and highlight differences" }
  }
]
```

### "enter invoice to SAP"

```json
[
  {
    "step": 1,
    "component": "pdf_parser",
    "params": { "file": "invoice.pdf" }
  },
  {
    "step": 2,
    "component": "llm_extractor",
    "params": {}
  },
  {
    "step": 3,
    "component": "validator",
    "params": {}
  },
  {
    "step": 4,
    "component": "api_caller",
    "params": { "system": "SAP", "endpoint": "/invoices" }
  }
]
```
