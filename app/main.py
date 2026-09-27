from fastapi import FastAPI

from app.agent import SalesAgent
from app.database import init_db
from app.models import ChatRequest, ChatResponse

app = FastAPI(
    title="LeadPilot — AI Sales Lead Agent",
    version="0.1.0",
)

agent = SalesAgent()
sessions: dict[str, list[dict]] = {}


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return {"name": "LeadPilot", "message": "AI Sales Lead Agent is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    history = sessions.setdefault(request.session_id, [])
    response = agent.respond(request.message, history)

    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": response})

    return ChatResponse(
        session_id=request.session_id,
        response=response,
    )
