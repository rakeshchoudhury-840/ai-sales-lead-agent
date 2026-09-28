from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent import SalesAgent
from app.database import init_db
from app.models import ChatRequest, ChatResponse


app = FastAPI(
    title="LeadPilot — AI Sales Lead Agent",
    version="0.1.0",
)

# Allow the frontend to communicate with the FastAPI backend.
# This is useful while developing locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agent = SalesAgent()

# Stores conversation history for each session.
sessions: dict[str, list[dict]] = {}


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return {
        "name": "LeadPilot",
        "message": "AI Sales Lead Agent is running",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Get existing conversation history or create a new one.
    history = sessions.setdefault(request.session_id, [])

    # Send the customer's message to the sales agent.
    response = agent.respond(
        request.message,
        history,
    )

    # Save the conversation.
    history.append(
        {
            "role": "user",
            "content": request.message,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    # Return the response to the frontend.
    return ChatResponse(
        session_id=request.session_id,
        response=response,
    )