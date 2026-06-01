# Sprint 2 Backlog

**Goal:** Make the system more reliable and easier to use

---

## Tasks

| # | Task | Priority |
|---|---|---|
| 1 | Fix email_reader module-level execution — wrap prints in `if __name__ == '__main__'` | High |
| 2 | Move APPROVED_VENDORS and CREDIT_LIMITS to a config file | High |
| 3 | Make `/run-workflow` async so the server doesn't block on long pipelines | High |
| 4 | Add few-shot examples to the LLM prompt to improve vendor extraction | High |
| 5 | Add GitHub Actions to run pytest on every push | Medium |
| 6 | Add pytest tests for executor chaining logic | Medium |
| 7 | Fix misleading due date error message (Issue #4) | Medium |
| 8 | Add `GET /workflows` endpoint to list past execution logs | Medium |
| 9 | Update React frontend to poll for live step-by-step updates | Low |
| 10 | Write end-to-end integration test using a real test PDF | Low |
