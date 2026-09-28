import json

from ollama import chat

from app.rag.knowledge import retrieve_knowledge
from app.tools import OPENAI_TOOLS, execute_tool


OLLAMA_MODEL = "qwen2.5:7b"


SYSTEM_PROMPT = """
You are LeadPilot, an AI sales assistant for a business.

Your job is to have natural, helpful, human-like sales conversations.

You are NOT a form-filling bot.
You are NOT a keyword-matching chatbot.

Understand the customer's meaning and conversation context.

IMPORTANT TOOL RULES:

Use business tools whenever the answer requires real business information.

Available tools include:
- product search
- stock checking
- price checking
- quotation calculation
- lead qualification
- lead creation
- follow-up generation

Never invent:
- prices
- stock
- quotations
- lead information
- order confirmations

Creating a sales lead is NOT the same as placing an order.

Never tell the customer that an order has been placed unless an actual
order tool confirms it.

CONVERSATION:

- Remember previous messages.
- Do not ask for information already provided.
- Ask follow-up questions only when necessary.
- Respond naturally to casual language.
- When enough information is available, use the appropriate tools.
- Keep responses concise and conversational.

LEAD INFORMATION:

Try to collect:
- product
- quantity
- budget per unit
- location
- urgency

When the customer has confirmed their requirement:
- qualify the lead
- create the sales lead
- do not claim that an order was placed.

You are a helpful sales representative.
"""


def is_lead_creation_requested(message: str) -> bool:
    """
    This is NOT used to understand the customer's conversation.

    It is only a safety gate for a database write.
    We require the customer to explicitly indicate that they want
    the sales lead created.
    """

    text = message.lower().strip()

    confirmation_phrases = [
        "create the sales lead",
        "create sales lead",
        "create the lead",
        "create a lead",
        "save the lead",
        "save this lead",
        "save my lead",
        "please create the lead",
        "please create the sales lead",
        "yes create the lead",
        "yes, create the lead",
        "yes create the sales lead",
        "yes, create the sales lead",
    ]

    return any(
        phrase in text
        for phrase in confirmation_phrases
    )


class SalesAgent:

    def __init__(self):
        print(
            f"LeadPilot using local Ollama model: {OLLAMA_MODEL}"
        )

    def respond(
        self,
        message: str,
        history: list[dict],
    ) -> tuple[str, dict | None]:

        knowledge = retrieve_knowledge(message)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        # Previous conversation
        for item in history:

            if item.get("role") in ["user", "assistant"]:

                messages.append(
                    {
                        "role": item["role"],
                        "content": item["content"],
                    }
                )

        # Current message
        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        # RAG knowledge
        if knowledge:

            knowledge_text = "\n\n".join(
                str(item)
                for item in knowledge
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Relevant LeadPilot business knowledge:\n\n"
                        + knowledge_text
                    ),
                }
            )

        created_lead = None
        qualification_result = None

        # -----------------------------------------
        # AI + tool calling
        # -----------------------------------------

        for _ in range(5):

            response = chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=OPENAI_TOOLS,
            )

            assistant_message = response.message

            # -------------------------------------
            # No tool call
            # -------------------------------------

            if not assistant_message.tool_calls:

                return (
                    assistant_message.content.strip(),
                    created_lead,
                )

            # Add assistant tool call
            messages.append(assistant_message)

            # -------------------------------------
            # Execute tools
            # -------------------------------------

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(
                    f"LeadPilot tool call: "
                    f"{tool_name}({arguments})"
                )

                try:

                    result = execute_tool(
                        tool_name,
                        arguments,
                    )

                    # Convert Pydantic objects
                    if hasattr(result, "model_dump"):

                        result = result.model_dump()

                    elif hasattr(result, "dict"):

                        result = result.dict()

                    # ---------------------------------
                    # Remember qualification result
                    # ---------------------------------

                    if tool_name == "qualify_lead":

                        qualification_result = result

                    # ---------------------------------
                    # Remember created lead
                    # ---------------------------------

                    if tool_name == "create_lead":

                        if isinstance(result, dict):

                            created_lead = result.get(
                                "lead",
                                result,
                            )

                except Exception as error:

                    result = {
                        "error": str(error)
                    }

                    print(
                        f"LeadPilot tool error: "
                        f"{tool_name} -> {error}"
                    )

                # Send tool result back to Qwen
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(
                            result,
                            default=str,
                        ),
                    }
                )

            # -----------------------------------------
            # IMPORTANT:
            #
            # If qualification succeeded and the
            # customer explicitly requested lead
            # creation, don't depend on Qwen to make
            # another tool call.
            # -----------------------------------------

            if (
                qualification_result
                and created_lead is None
                and is_lead_creation_requested(message)
            ):

                try:

                    lead_data = qualification_result

                    create_arguments = {
                        "product": lead_data.get(
                            "product",
                            arguments.get("product"),
                        ),
                        "quantity": lead_data.get(
                            "quantity",
                            arguments.get("quantity"),
                        ),
                        "budget_per_unit": lead_data.get(
                            "budget_per_unit",
                            arguments.get("budget_per_unit"),
                        ),
                        "location": lead_data.get(
                            "location",
                            arguments.get("location"),
                        ),
                        "urgency": lead_data.get(
                            "urgency",
                            arguments.get("urgency"),
                        ),
                        "lead_score": lead_data.get(
                            "lead_score",
                            0,
                        ),
                        "status": lead_data.get(
                            "status",
                            "New",
                        ),
                    }

                    print(
                        "LeadPilot automatic tool call: "
                        f"create_lead({create_arguments})"
                    )

                    result = execute_tool(
                        "create_lead",
                        create_arguments,
                    )

                    if hasattr(result, "model_dump"):

                        result = result.model_dump()

                    elif hasattr(result, "dict"):

                        result = result.dict()

                    if isinstance(result, dict):

                        created_lead = result.get(
                            "lead",
                            result,
                        )

                    # Tell Qwen that the lead was created.
                    messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                {
                                    "status": "created",
                                    "lead": created_lead,
                                },
                                default=str,
                            ),
                        }
                    )

                    # Ask Qwen for the final customer response.
                    final_response = chat(
                        model=OLLAMA_MODEL,
                        messages=messages,
                    )

                    final_text = (
                        final_response.message.content.strip()
                    )

                    return (
                        final_text,
                        created_lead,
                    )

                except Exception as error:

                    print(
                        "LeadPilot automatic lead creation error: "
                        f"{error}"
                    )

        # -----------------------------------------
        # Safety fallback
        # -----------------------------------------

        return (
            "I'm sorry, I wasn't able to complete "
            "that request. Could you please try again?",
            created_lead,
        )