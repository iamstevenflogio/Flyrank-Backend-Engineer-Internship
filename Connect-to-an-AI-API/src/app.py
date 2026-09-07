import os 
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.llm.schema import TriageRequest, TriageResponse

import json
from datetime import datetime, timezone

from pydantic import ValidationError

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "support-triage-v1.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

PROMPT_VERSION = "support-triage-v1"
LOGS_DIR = PROJECT_ROOT / "logs"
QUARANTINE_PATH = LOGS_DIR / "quarantine.jsonl"


client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
)

app = FastAPI()

def extract_json_object(raw_text: str) -> str:
    """Extract the outermost JSON object from the raw model output."""
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```")
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    start = cleaned.find("{")   
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or start > end:
        raise ValueError("Model output did not contain a JSON object")

    candidate = cleaned[start : end + 1]

    # Confirm if it is JSON before Pydantic validates its shape.
    json.loads(candidate)
    return candidate

def validate_model_output(raw_text: str) -> TriageResponse:
    """Parse model text, then validate it against the API schema."""
    json_text = extract_json_object(raw_text)
    return TriageResponse.model_validate_json(json_text)

def write_quarantine(
    *,
    request_text: str,
    raw_output: str, 
    error: str,
    attempt: int,
) -> None:
    """Append one failed model response to a JSON Lines quarantine log."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": PROMPT_VERSION,
        "attempt": attempt,
        "input": request_text,
        "raw_model_output": raw_output,
        "error": error,
    }

    with QUARANTINE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")

def request_repair(broken_output: str, validation_error: str) -> str:
    """Ask the model exactly once to repair a rejected output."""
    repair_message = f"""
Your previous answer was rejected for this reason:
{validation_error}

Previous answer:
{broken_output}

Return only corrected JSON matching the required schema.
""" 

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        message=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": repair_message},
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content or "" 

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

    raw_output = response.choices[0].message.content or ""

    try: 
        return validate_model_output(raw_output)
    
    except (ValueError, json.JSONDecodeError, ValidationError) as first_error:
        repaired_output = request_repair(
            broken_output=raw_output,
            validation_error=str(first_error),
        )

        try: 
            return validate_model_output(repaired_output)

        except (ValueError, json.JSONDecodeError, ValidationError) as second_error:
            write_quarantine(
                request_text=request.text,
                raw_output=repaired_output, 
                error=f"First attempt: {first_error}\nSecond attempt: {second_error}",
                attempt=2,
            )

            raise HTTPException(
                status_code=422,
                detail="The model returned an invalid classfication after one repair attempt. The response was quarantined.",
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

