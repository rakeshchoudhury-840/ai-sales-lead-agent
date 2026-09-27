# LeadPilot — AI Sales Lead Agent

A GitHub-ready portfolio starter designed around an Agentic AI Developer role requiring Python, FastAPI, FastMCP/MCP, LLM tool calling, structured output, RAG-style knowledge retrieval, lead qualification, multi-turn conversation, follow-up automation, and evaluation tests.

## What it does

LeadPilot acts as an AI sales representative for a fictional office-furniture SME. A customer can ask for products, quantities, prices, stock, quotations, and sales help.

## Architecture

Customer -> FastAPI /chat -> LLM Sales Agent -> Sales Tools / Knowledge -> Lead Qualification -> SQLite

The repository also contains a FastMCP server exposing the sales tools as MCP tools.

## Requirement mapping

- Python: all application code
- FastAPI: `app/main.py`
- FastMCP: `app/mcp/server.py`
- LLM / agent: `app/agent.py`
- Tool calling: `app/agent.py` and `app/tools.py`
- Structured output: `app/models.py`
- RAG-style retrieval: `app/rag/knowledge.py`
- Multi-turn conversation: session history in `app/main.py`
- Lead qualification: `app/services/sales.py`
- Follow-up automation: `generate_followup()`
- Evaluation/testing: `tests/`
- GitHub documentation: this README

## Setup

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

For AI mode:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6
DEMO_MODE=false
```

For no-API-key demo mode:

```env
DEMO_MODE=true
```

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

Run tests:

```bash
pytest
```

Run the MCP server:

```bash
python -m app.mcp.server
```

## Example request

```json
{
  "session_id": "demo-1",
  "message": "I need 20 office chairs for Hyderabad."
}
```

## Important

This is a portfolio starter, not a production CRM. Do not claim WhatsApp, voice, CRM, email sending, deployment, or production usage until those features are actually implemented. Never commit `.env` or API keys.
