# Week 2 Retrospective

**Date:** June 2026
**Format:** Keep / Drop / Try

---

## Keep

- **Component-based architecture** — splitting the system into email_reader, pdf_parser, llm_extractor, validator, api_caller made it easy to test and debug each part independently
- **Structured logging to logs/app.log** — having timestamps and component names in every log line made it easy to trace failures
- **Gemini model fallback** — automatically trying flash-lite → flash → 2.5-flash meant the pipeline never crashed on quota errors
- **GitHub Issues for bug tracking** — filing issues with steps to reproduce kept bugs organized and closeable with commit references
- **QA test matrix** — 15 structured test cases caught real bugs (negative amounts, swallowed FileNotFoundError) before they hit production
- **FastAPI + React separation** — keeping the backend and frontend decoupled made it easy to test the API independently with curl/Postman

---

## Drop

- **Module-level code in email_reader.py** — running `fetch_emails()` at import time caused unexpected prints every time anything imported the module; this should be in a `__main__` guard
- **Hardcoded test data in executor.py** — the `__main__` block with hardcoded invoice text is fragile; should use fixture files
- **Empty params `{}` from engine without chaining** — the engine generating steps with no params caused the executor to fail silently; the chaining fix was needed from the start
- **Debug print statements in llm_extractor** — replaced with logger calls in the final cleanup, but should have been logger from day one

---

## Try

- **Async FastAPI endpoints** — make `/run-workflow` async so long-running pipelines don't block the server
- **Webhook / polling for long jobs** — instead of waiting for the full pipeline in one HTTP response, return a job ID and let the frontend poll
- **More vendors in APPROVED_VENDORS** — the current list of 4 is hardcoded; move it to a config file or database
- **PDF attachment download directly from email** — currently requires a PDF to be in the inbox; try downloading from a Google Drive link in the email body
- **Better LLM prompt** — the current prompt misses vendor names on some real invoices; experiment with few-shot examples
- **CI/CD pipeline** — add GitHub Actions to run the 15 QA tests automatically on every push

---

## Summary

The MVP is working end-to-end: email → PDF → LLM → validate → SAP → Slack, exposed as a FastAPI API with a React frontend. The main pain points were around chaining data between components and quota limits on the free Gemini tier. Sprint 2 will focus on reliability, more real invoice types, and async execution.
