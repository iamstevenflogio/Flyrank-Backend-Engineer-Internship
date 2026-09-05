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
