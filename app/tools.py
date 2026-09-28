from app.services.sales import (
    calculate_quote,
    check_stock,
    create_lead,
    generate_followup,
    get_price,
    qualify_lead,
    search_product,
)


OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_product",
            "description": "Search the product catalog for a customer-requested product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product the customer is looking for.",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check whether the requested quantity is currently in stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product to check.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The number of units required.",
                    },
                },
                "required": ["product_name", "quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "Get the current catalog unit price for a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product whose price is needed.",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_quote",
            "description": (
                "Calculate a quotation for a product and quantity, "
                "including applicable bulk discounts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product for the quotation.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The number of units.",
                    },
                },
                "required": ["product_name", "quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "qualify_lead",
            "description": (
                "Evaluate a customer's sales lead using their product, "
                "quantity, budget, location, and urgency."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "The product the customer wants.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The requested quantity.",
                    },
                    "budget_per_unit": {
                        "type": "number",
                        "description": "The customer's budget per unit.",
                    },
                    "location": {
                        "type": "string",
                        "description": "The customer's delivery location.",
                    },
                    "urgency": {
                        "type": "string",
                        "description": "How soon the customer needs the product.",
                    },
                },
                "required": [
                    "product",
                    "quantity",
                    "budget_per_unit",
                    "location",
                    "urgency",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_lead",
            "description": (
                "Save a qualified sales lead to the LeadPilot database. "
                "Use this after the customer has confirmed their requirements."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "The product the customer wants.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The requested quantity.",
                    },
                    "budget_per_unit": {
                        "type": "number",
                        "description": "The customer's budget per unit.",
                    },
                    "location": {
                        "type": "string",
                        "description": "The customer's delivery location.",
                    },
                    "urgency": {
                        "type": "string",
                        "description": "How soon the customer needs the product.",
                    },
                    "lead_score": {
                        "type": "integer",
                        "description": "The qualification score for the lead.",
                    },
                    "status": {
                        "type": "string",
                        "description": "The current status of the lead.",
                    },
                },
                "required": [
                    "product",
                    "quantity",
                    "budget_per_unit",
                    "location",
                    "urgency",
                    "lead_score",
                    "status",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_followup",
            "description": (
                "Generate a professional follow-up message for a qualified "
                "sales lead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "The product the customer wants.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The requested quantity.",
                    },
                    "location": {
                        "type": "string",
                        "description": "The customer's delivery location.",
                    },
                    "urgency": {
                        "type": "string",
                        "description": "How soon the customer needs the product.",
                    },
                },
                "required": [
                    "product",
                    "quantity",
                    "location",
                    "urgency",
                ],
            },
        },
    },
]


FUNCTIONS = {
    "search_product": search_product,
    "check_stock": check_stock,
    "get_price": get_price,
    "calculate_quote": calculate_quote,
    "qualify_lead": qualify_lead,
    "create_lead": create_lead,
    "generate_followup": generate_followup,
}


def execute_tool(name: str, arguments: dict):
    if name not in FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")

    return FUNCTIONS[name](**arguments)