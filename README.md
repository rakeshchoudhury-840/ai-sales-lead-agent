# LeadPilot — AI Sales Lead Agent

LeadPilot is an AI-powered sales lead assistant built with Python and FastAPI.

It is designed to simulate how an AI sales agent can interact with potential customers, understand their requirements, qualify leads, and use business tools to support the sales process.

## Features

- Conversational AI sales assistant
- FastAPI backend
- Tool-calling architecture
- FastMCP tool server
- Product search
- Stock checking
- Price lookup
- Quote calculation
- Lead qualification
- Lead storage using SQLite
- Lightweight RAG knowledge retrieval
- Multi-turn conversation sessions
- Automated follow-up generation
- Basic evaluation tests
- Simple web chat interface

## Architecture

```text
Customer
   |
   v
Web Chat Interface
   |
   v
FastAPI
   |
   v
Sales Agent
   |
   +----> RAG Knowledge
   |
   +----> Business Tools
   |        |
   |        +--> Product Search
   |        +--> Stock Check
   |        +--> Price Lookup
   |        +--> Quote Calculation
   |
   +----> Lead Qualification
   |
   +----> Lead Storage
   |
   v
Sales Response