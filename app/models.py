from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(default="default")
    message: str


class Lead(BaseModel):
    customer_name: str | None = None
    product: str | None = None
    quantity: int | None = None
    budget_per_unit: float | None = None
    location: str | None = None
    urgency: str | None = None
    lead_score: int = 0
    status: str = "Unknown"


class ChatResponse(BaseModel):
    session_id: str
    response: str
    lead: Lead | None = None
