def _seed_product(client, quantity=50, sku="MOV-001"):
    response = client.post("/api/v1/products/", json={"sku": sku, "name": "Producto", "quantity": quantity, "min_stock": 10, "purchase_price": 2 if quantity > 0 else None})
    return response.json()


def test_increases_stock(client):
    product = _seed_product(client)
    response = client.post("/api/v1/movements/in", json={"product_id": product["id"], "quantity": 10, "unit_cost": 2})
    assert response.status_code == 201
    body = response.json()
    assert body["previous_quantity"] == 50
    assert body["new_quantity"] == 60
    assert client.get(f"/api/v1/products/{product['id']}").json()["quantity"] == 60


def test_out_decreases_stock(client):
    product = _seed_product(client)
    response = client.post("/api/v1/movements/out", json={"product_id": product["id"], "quantity": 20, "reason": "consumo"})
    assert response.status_code == 201
    assert response.json()["new_quantity"] == 30


def test_out_exceeding_stock_rejected(client):
    product = _seed_product(client)
    response = client.post("/api/v1/movements/out", json={"product_id": product["id"], "quantity": 999, "reason": "consumo"})
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]


def test_stock_never_negative(client):
    product = _seed_product(client, quantity=5)
    client.post("/api/v1/movements/out", json={"product_id": product["id"], "quantity": 999, "reason": "consumo"})
    assert client.get(f"/api/v1/products/{product['id']}").json()["quantity"] == 5


def test_zero_quantity_marks_agotado(client):
    product = _seed_product(client, quantity=5)
    client.post("/api/v1/movements/out", json={"product_id": product["id"], "quantity": 5, "reason": "consumo"})
    body = client.get(f"/api/v1/products/{product['id']}").json()
    assert body["status"] == "agotado"
    assert body["stock_condition"] == "agotado"


def test_stock_condition_recalculates_after_inventory_movements(client):
    product = _seed_product(client, quantity=2, sku="MOV-STOCK-COND")
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_condition"] == "stock_bajo"

    depleted = client.post("/api/v1/movements/out", json={
        "product_id": product["id"], "quantity": 2, "reason": "consumo",
    })
    assert depleted.status_code == 201
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_condition"] == "agotado"

    restocked = client.post("/api/v1/movements/in", json={
        "product_id": product["id"], "quantity": 1, "unit_cost": 2,
    })
    assert restocked.status_code == 201
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_condition"] == "stock_bajo"


def test_restock_reactivates_product(client):
    product = _seed_product(client, quantity=5)
    client.post("/api/v1/movements/out", json={"product_id": product["id"], "quantity": 5, "reason": "consumo"})
    client.post("/api/v1/movements/in", json={"product_id": product["id"], "quantity": 10, "unit_cost": 2})
    assert client.get(f"/api/v1/products/{product['id']}").json()["status"] == "vigente"


def test_movement_quantity_must_be_positive(client):
    product = _seed_product(client)
    response = client.post("/api/v1/movements/in", json={"product_id": product["id"], "quantity": 0})
    assert response.status_code == 422


def test_movements_history(client):
    product = _seed_product(client)
    client.post("/api/v1/movements/in", json={"product_id": product["id"], "quantity": 5, "unit_cost": 2})
    client.post("/api/v1/movements/out", json={"product_id": product["id"], "quantity": 2, "reason": "consumo"})
    body = client.get("/api/v1/movements/").json()
    assert body["total"] == 2
    assert body["items"][0]["movement_type"] == "OUT"
