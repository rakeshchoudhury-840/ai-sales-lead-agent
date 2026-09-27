from app.services.sales import calculate_quote, check_stock, qualify_lead, search_product


def test_search_product():
    result = search_product("office chair")
    assert result["matches"]
    assert result["matches"][0]["name"] == "Ergo Office Chair"


def test_stock_check():
    result = check_stock("office chair", 20)
    assert result["available"] is True


def test_quote():
    result = calculate_quote("office chair", 50)
    assert result["total"] == 182875.0
    assert result["discount_percent"] == 5.0


def test_lead_qualification():
    lead = qualify_lead(
        quantity=50,
        budget_per_unit=4000,
        urgency="2 weeks",
        product_match=True,
        location="Hyderabad",
    )
    assert lead.status == "Qualified"
    assert lead.lead_score == 100
