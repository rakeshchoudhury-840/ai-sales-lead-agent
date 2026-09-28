from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent import SalesAgent
from app.database import init_db
from app.models import ChatRequest, ChatResponse


app = FastAPI(
    title="LeadPilot — AI Sales Lead Agent",
    version="0.1.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Agent
# --------------------------------------------------

agent = SalesAgent()


# --------------------------------------------------
# Conversation memory
# --------------------------------------------------

sessions: dict[str, list[dict]] = {}


# --------------------------------------------------
# Startup
# --------------------------------------------------

@app.on_event("startup")
def startup():
    init_db()


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "name": "LeadPilot",
        "message": "AI Sales Lead Agent is running",
    }


# --------------------------------------------------
# Chat
# --------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # Get existing conversation history
    # or create a new session.
    history = sessions.setdefault(
        request.session_id,
        [],
    )

    # Send the customer message to the AI agent.
    response, lead = agent.respond(
        request.message,
        history,
    )

    # Save customer message.
    history.append(
        {
            "role": "user",
            "content": request.message,
        }
    )

    # Save AI response.
    history.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    # Return response + created lead.
    return ChatResponse(
        session_id=request.session_id,
        response=response,
        lead=lead,
    )