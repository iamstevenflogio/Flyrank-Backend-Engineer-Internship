import os 

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from llm.schema import TriageRequest, TriageResponse

app = FastAPI()

@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest) -> TriageResponse:
    if os.getenv("LLM_STUB") == "1":
        return TriageResponse(
            category="account",
            urgency="normal",
            confidence=0.95,
            reason="Stub response for endpoint testing",
        )

    return TriageResponse(
        category="other",
        urgency="low",
        confidence=0.0,
        reason="LLM integration is not enabled yet.",
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    first_error = exc.errors()[0]
    field_name = first_error["loc"][-1]

    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request",
            "field": field_name,
            "message": first_error["msg"],
        },
    )

