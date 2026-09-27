import json

from app.services.sales import (
    calculate_quote,
    check_stock,
    get_price,
    search_product,
)

OPENAI_TOOLS = [
    {
        "type": "function",
        "name": "search_product",
        "description": "Search the product catalog for a customer-requested product.",
        "parameters": {
            "type": "object",
            "properties": {"product_name": {"type": "string"}},
            "required": ["product_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "check_stock",
        "description": "Check whether the requested quantity is currently in stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "quantity": {"type": "integer"},
            },
            "required": ["product_name", "quantity"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_price",
        "description": "Get the current catalog unit price for a product.",
        "parameters": {
            "type": "object",
            "properties": {"product_name": {"type": "string"}},
            "required": ["product_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate_quote",
        "description": "Calculate a deterministic quotation for a product and quantity.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "quantity": {"type": "integer"},
            },
            "required": ["product_name", "quantity"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

FUNCTIONS = {
    "search_product": search_product,
    "check_stock": check_stock,
    "get_price": get_price,
    "calculate_quote": calculate_quote,
}


def execute_tool(name: str, arguments: dict):
    if name not in FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")
    return FUNCTIONS[name](**arguments)
