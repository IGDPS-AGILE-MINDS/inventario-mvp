def _create_product(client, sku, quantity, min_stock):
    response = client.post("/api/v1/products/", json={
        "sku": sku,
        "name": sku,
        "quantity": quantity,
        "min_stock": min_stock,
        "purchase_price": 2 if quantity > 0 else None,
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_dashboard_counts_low_and_out_of_stock_separately_and_recalculates(client):
    low = _create_product(client, "DASH-LOW", quantity=2, min_stock=5)
    exhausted = _create_product(client, "DASH-OUT", quantity=0, min_stock=5)
    normal = _create_product(client, "DASH-NORMAL", quantity=8, min_stock=5)

    summary = client.get("/api/v1/dashboard/summary").json()
    assert summary["low_stock"] == 1
    assert summary["out_of_stock"] == 1

    client.patch(f"/api/v1/products/{normal['id']}", json={"min_stock": 8})
    summary = client.get("/api/v1/dashboard/summary").json()
    assert summary["low_stock"] == 2
    assert summary["out_of_stock"] == 1

    movement = client.post("/api/v1/movements/out", json={
        "product_id": low["id"], "quantity": 2, "reason": "consumo",
    })
    assert movement.status_code == 201
    summary = client.get("/api/v1/dashboard/summary").json()
    assert summary["low_stock"] == 1
    assert summary["out_of_stock"] == 2
    assert client.get(f"/api/v1/products/{exhausted['id']}").json()["stock_condition"] == "agotado"
