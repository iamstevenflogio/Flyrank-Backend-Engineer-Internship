from enum import Enum

from pydantic import BaseModel, Field

class TriageRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=2000,
        description="Software support message to classify",
    )

class Category(str, Enum):
    billing = "billing"
    bug = "bug"
    feature = "feature"
    account = "account"
    other = "other"

class Urgency(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"

class TriageResponse(BaseModel):
    category: Category
    urgency: Urgency
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=300)