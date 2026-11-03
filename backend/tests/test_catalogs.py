def test_category_crud_and_duplicate_name(client):
    category = client.post("/api/v1/categories/", json={"name": "Lácteos"})
    assert category.status_code == 201
    category_id = category.json()["id"]
    assert client.get("/api/v1/categories/").json()[0]["name"] == "Lácteos"
    assert client.post("/api/v1/categories/", json={"name": "Lácteos"}).status_code == 400
    assert client.put(f"/api/v1/categories/{category_id}", json={"name": "Refrigerados"}).status_code == 200
    assert client.delete(f"/api/v1/categories/{category_id}").status_code == 204


def test_category_cannot_be_deleted_while_products_use_it(client):
    category = client.post("/api/v1/categories/", json={"name": "Bebidas"}).json()
    product = client.post("/api/v1/products/", json={
        "sku": "CAT-001", "name": "Agua", "category_id": category["id"], "quantity": 0,
    })
    assert product.status_code == 201
    response = client.delete(f"/api/v1/categories/{category['id']}")
    assert response.status_code == 409
    assert client.get("/api/v1/categories/").json()[0]["id"] == category["id"]


def test_supplier_crud_and_duplicate_name(client):
    supplier = client.post("/api/v1/suppliers/", json={
        "name": "Distribuidora Uno", "contact_name": "Ana", "email": "ana@example.com",
        "phone": "123", "address": "Calle 1",
    })
    assert supplier.status_code == 201
    supplier_id = supplier.json()["id"]
    assert client.get("/api/v1/suppliers/").json()[0]["contact_name"] == "Ana"
    assert client.post("/api/v1/suppliers/", json={"name": "Distribuidora Uno"}).status_code == 400
    assert client.put(f"/api/v1/suppliers/{supplier_id}", json={"phone": "456"}).status_code == 200
    assert client.delete(f"/api/v1/suppliers/{supplier_id}").status_code == 204


def test_supplier_email_and_blank_name_validation(client):
    assert client.post("/api/v1/suppliers/", json={"name": "  "}).status_code == 422
    assert client.post("/api/v1/suppliers/", json={"name": "Proveedor", "email": "no-es-correo"}).status_code == 422


def test_supplier_cannot_be_deleted_while_products_use_it(client):
    supplier = client.post("/api/v1/suppliers/", json={"name": "Distribuidora Dos"}).json()
    product = client.post("/api/v1/products/", json={
        "sku": "SUP-001", "name": "Arroz", "supplier_id": supplier["id"], "quantity": 0,
    })
    assert product.status_code == 201
    response = client.delete(f"/api/v1/suppliers/{supplier['id']}")
    assert response.status_code == 409
    assert client.get("/api/v1/suppliers/").json()[0]["id"] == supplier["id"]
