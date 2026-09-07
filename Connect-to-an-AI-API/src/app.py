import os 
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.llm.schema import TriageRequest, TriageResponse

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "support-triage-v1.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
)

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

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.text},
        ],
        temperature=0,
    )

    raw_output = response.choices[0].message.content
    print(raw_output)
    return TriageResponse.model_validate_json(raw_output)

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

