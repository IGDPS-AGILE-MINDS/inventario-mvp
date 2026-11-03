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
    assert negative.status_code == 422
    assert null_name.status_code == 422


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


def test_delete_product(client):
    product = _create_product(client)
    response = client.delete(f"/api/v1/products/{product['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/products/{product['id']}").status_code == 404


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
