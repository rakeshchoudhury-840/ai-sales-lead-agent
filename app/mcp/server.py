from fastmcp import FastMCP

from app.models import Lead
from app.services.sales import (
    calculate_quote,
    check_stock,
    create_lead,
    generate_followup,
    get_price,
    qualify_lead,
    search_product,
)

mcp = FastMCP("LeadPilot Sales Tools")


@mcp.tool
def search_product_tool(product_name: str) -> dict:
    """Search the office-furniture product catalog."""
    return search_product(product_name)


@mcp.tool
def check_stock_tool(product_name: str, quantity: int) -> dict:
    """Check whether a requested quantity is in stock."""
    return check_stock(product_name, quantity)


@mcp.tool
def get_price_tool(product_name: str) -> dict:
    """Get the catalog unit price for a product."""
    return get_price(product_name)


@mcp.tool
def calculate_quote_tool(product_name: str, quantity: int) -> dict:
    """Calculate a quotation using deterministic business rules."""
    return calculate_quote(product_name, quantity)


@mcp.tool
def qualify_lead_tool(
    quantity: int | None = None,
    budget_per_unit: float | None = None,
    urgency: str | None = None,
    product_match: bool = True,
    location: str | None = None,
) -> dict:
    """Score a sales lead using deterministic qualification rules."""
    return qualify_lead(
        quantity=quantity,
        budget_per_unit=budget_per_unit,
        urgency=urgency,
        product_match=product_match,
        location=location,
    ).model_dump()


@mcp.tool
def create_lead_tool(
    session_id: str,
    product: str | None = None,
    quantity: int | None = None,
    budget_per_unit: float | None = None,
    location: str | None = None,
    urgency: str | None = None,
    lead_score: int = 0,
    status: str = "Unknown",
) -> dict:
    """Persist a sales lead in SQLite."""
    lead = Lead(
        product=product,
        quantity=quantity,
        budget_per_unit=budget_per_unit,
        location=location,
        urgency=urgency,
        lead_score=lead_score,
        status=status,
    )
    return create_lead(session_id, lead)


@mcp.tool
def generate_followup_tool(
    product: str | None = None,
    status: str = "Warm",
    lead_score: int = 0,
) -> str:
    """Generate a concise sales follow-up message."""
    lead = Lead(product=product, status=status, lead_score=lead_score)
    return generate_followup(lead)


if __name__ == "__main__":
    mcp.run()
