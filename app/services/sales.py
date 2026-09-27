from app.database import save_lead
from app.models import Lead

PRODUCTS = {
    "office chair": {
        "name": "Ergo Office Chair",
        "price": 3850,
        "stock": 72,
        "description": "Ergonomic mesh office chair with adjustable height.",
    },
    "executive chair": {
        "name": "Executive Pro Chair",
        "price": 6200,
        "stock": 25,
        "description": "High-back executive chair with padded arms.",
    },
    "training chair": {
        "name": "Training Chair",
        "price": 2200,
        "stock": 120,
        "description": "Stackable chair for training rooms and classrooms.",
    },
}


def search_product(product_name: str) -> dict:
    query = product_name.lower().strip()
    matches = []
    for key, product in PRODUCTS.items():
        if query in key or query in product["name"].lower():
            matches.append(product | {"key": key})
    return {"matches": matches}


def check_stock(product_name: str, quantity: int) -> dict:
    result = search_product(product_name)
    if not result["matches"]:
        return {"available": False, "reason": "Product not found"}
    product = result["matches"][0]
    return {
        "product": product["name"],
        "requested_quantity": quantity,
        "stock": product["stock"],
        "available": product["stock"] >= quantity,
    }


def get_price(product_name: str) -> dict:
    result = search_product(product_name)
    if not result["matches"]:
        return {"found": False}
    product = result["matches"][0]
    return {"found": True, "product": product["name"], "unit_price": product["price"]}


def calculate_quote(product_name: str, quantity: int) -> dict:
    price = get_price(product_name)
    if not price.get("found"):
        return {"error": "Product not found"}

    unit_price = price["unit_price"]
    subtotal = unit_price * quantity
    discount = 0.05 if quantity >= 25 else 0.0
    discount_amount = subtotal * discount
    total = subtotal - discount_amount

    return {
        "product": price["product"],
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_percent": discount * 100,
        "total": round(total, 2),
    }


def qualify_lead(
    quantity: int | None,
    budget_per_unit: float | None,
    urgency: str | None,
    product_match: bool = True,
    location: str | None = None,
) -> Lead:
    score = 0

    if quantity and quantity >= 25:
        score += 25
    elif quantity and quantity >= 10:
        score += 15

    if budget_per_unit and budget_per_unit > 0:
        score += 20

    if urgency:
        score += 20

    if product_match:
        score += 20

    if location:
        score += 15

    status = "Qualified" if score >= 70 else "Warm" if score >= 40 else "Cold"

    return Lead(
        quantity=quantity,
        budget_per_unit=budget_per_unit,
        urgency=urgency,
        location=location,
        lead_score=min(score, 100),
        status=status,
    )


def create_lead(session_id: str, lead: Lead) -> dict:
    lead_id = save_lead(session_id, lead.model_dump())
    return {"lead_id": lead_id, "status": "saved", "lead": lead.model_dump()}


def generate_followup(lead: Lead) -> str:
    product = lead.product or "your requirement"
    if lead.status == "Qualified":
        return (
            f"Hi! Just following up on your {product} requirement. "
            "Would you like me to prepare the final quotation?"
        )
    return (
        f"Hi! Just checking in about your {product} requirement. "
        "Let me know your quantity, budget, and preferred timeline."
    )
