from app.database import save_lead
from app.models import Lead


# ============================================================
# PRODUCT CATALOG
# ============================================================

PRODUCTS = {
    "office chair": {
        "name": "Ergo Office Chair",
        "price": 3850,
        "stock": 72,
        "description": (
            "Ergonomic mesh office chair with adjustable height."
        ),
    },
    "executive chair": {
        "name": "Executive Pro Chair",
        "price": 6200,
        "stock": 25,
        "description": (
            "High-back executive chair with padded arms."
        ),
    },
    "training chair": {
        "name": "Training Chair",
        "price": 2200,
        "stock": 120,
        "description": (
            "Stackable chair for training rooms and classrooms."
        ),
    },
}


# ============================================================
# PRODUCT NAME NORMALIZATION
# ============================================================

def normalize_product_name(product_name: str) -> str:
    """
    Normalize customer/product input so small differences in
    wording do not cause a product lookup failure.
    """

    if not product_name:
        return ""

    query = product_name.lower().strip()

    # Remove common punctuation.
    for character in [",", ".", "!", "?", "-", "_"]:
        query = query.replace(character, " ")

    # Normalize repeated spaces.
    query = " ".join(query.split())

    # Common customer expressions.
    aliases = {
        "ergo chair": "ergo office chair",
        "ergonomic chair": "ergo office chair",
        "ergonomic office chair": "ergo office chair",
        "office chairs": "office chair",
        "executive chairs": "executive chair",
        "training chairs": "training chair",
    }

    return aliases.get(query, query)


# ============================================================
# SEARCH PRODUCT
# ============================================================

def search_product(product_name: str) -> dict:
    """
    Search the product catalog.

    Supports:
    - exact product names
    - catalog keys
    - partial names
    - common aliases
    """

    query = normalize_product_name(product_name)

    if not query:
        return {
            "matches": [],
            "message": "No product name was provided.",
        }

    matches = []

    for key, product in PRODUCTS.items():

        key_normalized = normalize_product_name(key)
        name_normalized = normalize_product_name(
            product["name"]
        )

        # Exact match.
        if (
            query == key_normalized
            or query == name_normalized
        ):
            matches.append(
                product | {"key": key}
            )
            continue

        # Partial match.
        if (
            query in key_normalized
            or key_normalized in query
            or query in name_normalized
            or name_normalized in query
        ):
            matches.append(
                product | {"key": key}
            )

    return {
        "query": product_name,
        "matches": matches,
    }


# ============================================================
# CHECK STOCK
# ============================================================

def check_stock(
    product_name: str,
    quantity: int,
) -> dict:

    result = search_product(product_name)

    if not result["matches"]:
        return {
            "available": False,
            "reason": "Product not found",
            "product": product_name,
        }

    product = result["matches"][0]

    return {
        "available": product["stock"] >= quantity,
        "product": product["name"],
        "requested_quantity": quantity,
        "stock": product["stock"],
        "description": product["description"],
    }


# ============================================================
# GET PRICE
# ============================================================

def get_price(product_name: str) -> dict:

    result = search_product(product_name)

    if not result["matches"]:
        return {
            "found": False,
            "product": product_name,
            "reason": "Product not found",
        }

    product = result["matches"][0]

    return {
        "found": True,
        "product": product["name"],
        "unit_price": product["price"],
        "description": product["description"],
    }


# ============================================================
# CALCULATE QUOTE
# ============================================================

def calculate_quote(
    product_name: str,
    quantity: int,
) -> dict:

    if quantity <= 0:
        return {
            "error": "Quantity must be greater than zero."
        }

    price = get_price(product_name)

    if not price.get("found"):
        return {
            "error": "Product not found",
            "product": product_name,
        }

    unit_price = price["unit_price"]

    subtotal = unit_price * quantity

    # 5% bulk discount for 25 or more units.
    discount_percent = 5.0 if quantity >= 25 else 0.0

    discount_amount = (
        subtotal * discount_percent / 100
    )

    total = subtotal - discount_amount

    return {
        "product": price["product"],
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": round(subtotal, 2),
        "discount_percent": discount_percent,
        "discount_amount": round(
            discount_amount,
            2,
        ),
        "total": round(total, 2),
    }


# ============================================================
# QUALIFY LEAD
# ============================================================

def qualify_lead(
    product: str | None = None,
    quantity: int | None = None,
    budget_per_unit: float | None = None,
    location: str | None = None,
    urgency: str | None = None,
    product_match: bool = True,
) -> Lead:

    score = 0

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    if quantity and quantity >= 25:
        score += 25

    elif quantity and quantity >= 10:
        score += 15

    elif quantity and quantity > 0:
        score += 5

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    if budget_per_unit and budget_per_unit > 0:
        score += 20

    # --------------------------------------------------------
    # Urgency
    # --------------------------------------------------------

    if urgency:
        score += 20

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    if product and product_match:
        score += 20

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    if location:
        score += 15

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if score >= 70:
        status = "Qualified"

    elif score >= 40:
        status = "Warm"

    else:
        status = "Cold"

    # --------------------------------------------------------
    # Build Lead object
    # --------------------------------------------------------

    return Lead(
        product=product,
        quantity=quantity,
        budget_per_unit=budget_per_unit,
        urgency=urgency,
        location=location,
        lead_score=min(score, 100),
        status=status,
    )


# ============================================================
# CREATE LEAD
# ============================================================

def create_lead(
    product: str | None = None,
    quantity: int | None = None,
    budget_per_unit: float | None = None,
    location: str | None = None,
    urgency: str | None = None,
    lead_score: int = 0,
    status: str = "Warm",
    session_id: str = "default",
) -> dict:

    lead = Lead(
        product=product,
        quantity=quantity,
        budget_per_unit=budget_per_unit,
        location=location,
        urgency=urgency,
        lead_score=lead_score,
        status=status,
    )

    lead_id = save_lead(
        session_id,
        lead.model_dump(),
    )

    return {
        "lead_id": lead_id,
        "status": "saved",
        "lead": lead.model_dump(),
    }


# ============================================================
# GENERATE FOLLOW-UP
# ============================================================

def generate_followup(
    product: str | None = None,
    quantity: int | None = None,
    location: str | None = None,
    urgency: str | None = None,
    lead: Lead | None = None,
) -> str:

    # --------------------------------------------------------
    # Support both direct arguments and a Lead object.
    # --------------------------------------------------------

    if lead is not None:
        product = lead.product
        quantity = lead.quantity
        location = lead.location
        urgency = lead.urgency
        status = lead.status

    else:
        status = "Warm"

    product_text = product or "your requirement"

    quantity_text = (
        f"{quantity} units"
        if quantity
        else "your requested quantity"
    )

    location_text = (
        f" in {location}"
        if location
        else ""
    )

    urgency_text = (
        f" for {urgency}"
        if urgency
        else ""
    )

    if status == "Qualified":
        return (
            f"Hi! Just following up on your "
            f"{quantity_text} of {product_text}"
            f"{location_text}{urgency_text}. "
            "Would you like us to proceed with the final quotation?"
        )

    return (
        f"Hi! Just checking in about your "
        f"{quantity_text} of {product_text}"
        f"{location_text}{urgency_text}. "
        "Let me know if you'd like to continue."
    )