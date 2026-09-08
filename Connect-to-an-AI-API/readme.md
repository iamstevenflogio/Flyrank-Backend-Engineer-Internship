# Support Message Triage API

Classifies a software support message by category and urgency.

## Example input

```json
{
  "text": "I cannot log in after resetting my password."
}
```

## Example stub response

```json
{
  "category": "account",
  "urgency": "normal",
  "confidence": 0.95,
  "reason": "Stub response for local endpoint testing."
}
```

## Example requests

### Valid request

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/triage" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"I cannot log in after resetting my password."}'
```

### Invalid request: missing `text`

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/triage" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{}'
```

Expected result: HTTP 400 with a JSON error identifying the missing `text` field.

## LLM reliability policy

- Each LLM request has a 30-second timeout.
- SDK retries are disabled with `max_retries=0`.
- The application retries only timeouts, connection errors, HTTP 429 responses, and HTTP 5xx responses.
- Retries use exponential backoff with jitter and allow at most two retries after the first attempt.
- HTTP 400, 401, and 403 errors are not retried.
- Set `LLM_ENABLED=false` to disable live model calls and return a deterministic fallback.
- Per-call token usage, duration, repair status, and attempt number are recorded in `logs/llm-calls.jsonl`.

## Evaluation

- Evaluation command: `python scripts/run_evals.py`
- Final completed baseline: `4/8 (50.0%)`
- Fields evaluated: `category` and `urgency`
- Prompt version: `support-triage-v1`

The endpoint correctly returned valid classifications for four cases. On other cases, the `openrouter/free` route produced malformed, incomplete, empty, unrelated, or slow output. The API safely handled these cases through schema validation, a single repair attempt, quarantine logging, and controlled error responses rather than returning unvalidated model content.
