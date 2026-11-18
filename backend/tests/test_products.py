def _create_product(client, sku="TEST-001", quantity=50, min_stock=10):
    response = client.post("/api/v1/products/", json={
        "sku": sku, "name": "Producto de prueba", "quantity": quantity, "min_stock": min_stock,
        "purchase_price": 2 if quantity > 0 else None,
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_create_product(client):
    product = _create_product(client)
    assert product["quantity"] == 50
    assert product["expiration_status"] == "sin_fecha"
    assert product["weighted_average_cost"] == 2


def test_initial_cost_required_only_when_stock_is_created(client):
    missing_cost = client.post("/api/v1/products/", json={"sku": "COST-001", "name": "Con stock", "quantity": 3})
    no_stock = client.post("/api/v1/products/", json={"sku": "COST-002", "name": "Sin stock", "quantity": 0})
    assert missing_cost.status_code == 422
    assert no_stock.status_code == 201
    assert no_stock.json()["weighted_average_cost"] is None


def test_stock_condition_distinguishes_exhausted_low_and_normal_stock(client):
    exhausted = _create_product(client, sku="STOCK-000", quantity=0, min_stock=10)
    low = _create_product(client, sku="STOCK-001", quantity=1, min_stock=10)
    at_minimum = _create_product(client, sku="STOCK-010", quantity=10, min_stock=10)
    normal = _create_product(client, sku="STOCK-011", quantity=11, min_stock=10)

    assert exhausted["stock_condition"] == "agotado"
    assert exhausted["status"] == "agotado"
    assert low["stock_condition"] == "stock_bajo"
    assert at_minimum["stock_condition"] == "stock_bajo"
    assert normal["stock_condition"] == "normal"


def test_stock_condition_recalculates_when_minimum_changes(client):
    product = _create_product(client, sku="STOCK-CHANGE", quantity=12, min_stock=10)
    assert product["stock_condition"] == "normal"

    low = client.patch(f"/api/v1/products/{product['id']}", json={"min_stock": 12}).json()
    normal = client.patch(f"/api/v1/products/{product['id']}", json={"min_stock": 11}).json()
    assert low["stock_condition"] == "stock_bajo"
    assert normal["stock_condition"] == "normal"
    assert normal["quantity"] == 12


def test_stock_condition_does_not_change_active_flag(client):
    product = _create_product(client, sku="STOCK-INACTIVE", quantity=5, min_stock=2)
    client.patch(f"/api/v1/products/{product['id']}/deactivate")

    updated = client.patch(f"/api/v1/products/{product['id']}", json={"min_stock": 5}).json()

    assert updated["stock_condition"] == "stock_bajo"
    assert updated["is_active"] is False


def test_negative_initial_cost_is_rejected(client):
    response = client.post("/api/v1/products/", json={
        "sku": "COST-003", "name": "Costo negativo", "quantity": 1, "purchase_price": -1,
    })
    assert response.status_code == 422
    assert client.get("/api/v1/products/").json()["total"] == 0


def test_update_rejects_negative_or_null_required_fields(client):
    product = _create_product(client)
    negative = client.put(f"/api/v1/products/{product['id']}", json={"quantity": -1})
    null_name = client.put(f"/api/v1/products/{product['id']}", json={"name": None})
    blank_sku = client.patch(f"/api/v1/products/{product['id']}", json={"sku": "   "})
    assert negative.status_code == 422
    assert null_name.status_code == 422
    assert blank_sku.status_code == 422


def test_invalid_product_relations_are_rejected(client):
    response = client.post("/api/v1/products/", json={"sku": "REL-001", "name": "Producto", "category_id": 999})
    assert response.status_code == 400
    assert client.get("/api/v1/products/").json()["total"] == 0


def test_duplicate_sku_rejected(client):
    _create_product(client)
    response = client.post("/api/v1/products/", json={"sku": "TEST-001", "name": "Otro"})
    assert response.status_code == 400


def test_negative_quantity_rejected(client):
    response = client.post("/api/v1/products/", json={"sku": "TEST-002", "name": "X", "quantity": -5})
    assert response.status_code == 422


def test_update_product(client):
    product = _create_product(client)
    response = client.put(f"/api/v1/products/{product['id']}", json={"name": "Renombrado"})
    assert response.status_code == 200
    assert response.json()["name"] == "Renombrado"


def test_partial_update_preserves_omitted_fields(client):
    product = _create_product(client)
    response = client.patch(f"/api/v1/products/{product['id']}", json={"description": "Nuevo detalle"})
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Nuevo detalle"
    assert body["name"] == product["name"]
    assert body["sku"] == product["sku"]
    assert body["quantity"] == product["quantity"]
    assert body["min_stock"] == product["min_stock"]
    assert body["sale_price"] == product["sale_price"]
    assert body["weighted_average_cost"] == product["weighted_average_cost"]


def test_product_edit_cannot_change_inventory_or_average_cost(client):
    product = _create_product(client)
    for protected_field, value in (("quantity", 0), ("purchase_price", 999), ("weighted_average_cost", 999)):
        response = client.patch(f"/api/v1/products/{product['id']}", json={protected_field: value})
        assert response.status_code == 422
    current = client.get(f"/api/v1/products/{product['id']}").json()
    assert current["quantity"] == product["quantity"]
    assert current["weighted_average_cost"] == product["weighted_average_cost"]


def test_partial_update_enforces_sku_uniqueness_without_mutating_product(client):
    first = _create_product(client, sku="UNIQUE-001")
    second = _create_product(client, sku="UNIQUE-002")
    response = client.patch(f"/api/v1/products/{second['id']}", json={"sku": first["sku"], "name": "No debe guardarse"})
    assert response.status_code == 400
    current = client.get(f"/api/v1/products/{second['id']}").json()
    assert current["sku"] == second["sku"]
    assert current["name"] == second["name"]


def test_missing_product_update_does_not_mutate_other_products(client):
    product = _create_product(client)
    response = client.patch("/api/v1/products/9999", json={"name": "Cambio"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Producto no encontrado"
    assert client.get(f"/api/v1/products/{product['id']}").json()["name"] == product["name"]


def test_delete_product(client):
    product = _create_product(client)
    response = client.delete(f"/api/v1/products/{product['id']}")
    assert response.status_code == 204
    persisted = client.get(f"/api/v1/products/{product['id']}")
    assert persisted.status_code == 200
    assert persisted.json()["is_active"] is False


def test_delete_with_movements_deactivates_and_preserves_history(client):
    product = _create_product(client)
    movement = client.post("/api/v1/movements/out", json={
        "product_id": product["id"], "quantity": 3, "reason": "consumo",
    })
    assert movement.status_code == 201

    response = client.delete(f"/api/v1/products/{product['id']}")

    assert response.status_code == 204
    persisted = client.get(f"/api/v1/products/{product['id']}")
    assert persisted.status_code == 200
    assert persisted.json()["is_active"] is False
    history = client.get("/api/v1/movements/", params={"product_id": product["id"]}).json()
    assert history["total"] == 1
    assert history["items"][0]["product_name"] == product["name"]
    assert client.post("/api/v1/movements/in", json={
        "product_id": product["id"], "quantity": 1, "unit_cost": 2,
    }).status_code == 409
    assert client.post("/api/v1/movements/out", json={
        "product_id": product["id"], "quantity": 1, "reason": "consumo",
    }).status_code == 409
    assert client.get("/api/v1/products/", params={"is_active": "true"}).json()["total"] == 0
    assert client.get("/api/v1/products/", params={"is_active": "false"}).json()["total"] == 1


def test_deactivate_endpoint_keeps_product_visible_in_default_list(client):
    product = _create_product(client)
    response = client.patch(f"/api/v1/products/{product['id']}/deactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    listed = client.get("/api/v1/products/").json()
    assert listed["total"] == 1
    assert listed["items"][0]["id"] == product["id"]


def test_missing_product_delete_does_not_mutate_other_products(client):
    product = _create_product(client)
    response = client.delete("/api/v1/products/9999")
    assert response.status_code == 404
    persisted = client.get(f"/api/v1/products/{product['id']}").json()
    assert persisted["is_active"] is True


def test_search_and_pagination(client):
    for i in range(15):
        _create_product(client, sku=f"BULK-{i:03d}", quantity=0)
    response = client.get("/api/v1/products/", params={"search": "bulk", "limit": 10})
    body = response.json()
    assert body["total"] == 15
    assert len(body["items"]) == 10
    response = client.get("/api/v1/products/", params={"search": "bulk", "limit": 10, "offset": 10})
    assert len(response.json()["items"]) == 5


def test_search_matches_name_and_sku_case_insensitively(client):
    _create_product(client, sku="AbC-123", quantity=0)
    by_name = client.get("/api/v1/products/", params={"search": "PRODUCTO DE PRUEBA"}).json()
    by_sku = client.get("/api/v1/products/", params={"search": "abc-123"}).json()
    assert by_name["total"] == 1
    assert by_sku["total"] == 1
