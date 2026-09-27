import json

from openai import OpenAI

from app.config import DEMO_MODE, OPENAI_API_KEY, OPENAI_MODEL
from app.rag.knowledge import retrieve_knowledge
from app.tools import OPENAI_TOOLS, execute_tool


SYSTEM_PROMPT = """
You are LeadPilot, an AI sales representative for a fictional Indian office-furniture SME.

Goals:
- Have a natural, helpful sales conversation.
- Understand product, quantity, budget, location, and timeline.
- Ask concise follow-up questions when important information is missing.
- Use product tools before claiming a price or stock level.
- Never invent stock, prices, discounts, or policies.
- Recommend products only from tool results.
- Help move a qualified customer toward a quotation.
- State that quotations are estimates until confirmed by a human salesperson.
"""


class SalesAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def respond(self, message: str, history: list[dict]) -> str:
        if DEMO_MODE or not self.client:
            return self.demo_response(message)

        knowledge = retrieve_knowledge(message)

        input_items = history + [{"role": "user", "content": message}]

        if knowledge:
            input_items.insert(
                0,
                {
                    "role": "developer",
                    "content": "Relevant company knowledge:\n"
                    + "\n\n".join(knowledge),
                },
            )

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=input_items,
            tools=OPENAI_TOOLS,
        )

        tool_outputs = []

        for item in response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)
                result = execute_tool(item.name, args)

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                )

        if tool_outputs:
            follow_up = self.client.responses.create(
                model=OPENAI_MODEL,
                instructions=SYSTEM_PROMPT,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=OPENAI_TOOLS,
            )

            return follow_up.output_text

        return response.output_text

    def demo_response(self, message: str) -> str:
        message_lower = message.lower()

        if "chair" in message_lower:
            return (
                "Sure! We can help with office chairs. "
                "Could you tell me the quantity you need, "
                "your delivery location, and your approximate budget per chair?"
            )

        if "price" in message_lower or "cost" in message_lower:
            return (
                "I can help you check pricing. "
                "Please tell me which product you are interested in and the quantity."
            )

        if "hello" in message_lower or "hi" in message_lower:
            return (
                "Hello! 👋 I'm LeadPilot, your AI sales assistant. "
                "What product are you looking for today?"
            )

        return (
            "I'd be happy to help with your purchase. "
            "Please tell me the product, quantity, delivery location, "
            "and approximate budget."
        )