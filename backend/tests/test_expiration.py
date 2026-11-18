from datetime import date, timedelta

from app.services.expiration import expiration_status


def test_expired():
    yesterday = date.today() - timedelta(days=1)
    assert expiration_status(yesterday, 30) == "vencido"


def test_expiring_soon():
    in_10_days = date.today() + timedelta(days=10)
    assert expiration_status(in_10_days, 30) == "proximo_a_vencer"


def test_still_valid():
    in_60_days = date.today() + timedelta(days=60)
    assert expiration_status(in_60_days, 30) == "vigente"


def test_no_date():
    assert expiration_status(None, 30) == "sin_fecha"


def test_warning_days_respected():
    in_40_days = date.today() + timedelta(days=40)
    assert expiration_status(in_40_days, 30) == "vigente"
    assert expiration_status(in_40_days, 45) == "proximo_a_vencer"


def test_settings_update(client):
    response = client.get("/api/v1/settings/")
    assert response.status_code == 200
    response = client.put("/api/v1/settings/", json={"expiration_warning_days": 45})
    assert response.status_code == 200
    assert response.json()["expiration_warning_days"] == 45
    assert client.get("/api/v1/settings/").json()["expiration_warning_days"] == 45


def test_settings_validation(client):
    response = client.put("/api/v1/settings/", json={"expiration_warning_days": 999})
    assert response.status_code == 422


def test_expiration_filter(client):
    today = date.today()
    expiring = today + timedelta(days=10)
    client.post("/api/v1/products/", json={"sku": "EXP-001", "name": "Por vencer", "expiration_date": expiring.isoformat()})
    client.post("/api/v1/products/", json={"sku": "EXP-002", "name": "Vencido", "expiration_date": (today - timedelta(days=1)).isoformat()})
    body = client.get("/api/v1/products/", params={"expiration": "proximo_a_vencer"}).json()
    assert body["total"] == 1
    assert body["items"][0]["sku"] == "EXP-001"
    body = client.get("/api/v1/products/", params={"expiration": "vencido"}).json()
    assert body["total"] == 1
    assert body["items"][0]["sku"] == "EXP-002"


def test_expiration_filter_vigente(client):
    in_60_days = date.today() + timedelta(days=60)
    client.post("/api/v1/products/", json={"sku": "VIG-001", "name": "Vigente", "expiration_date": in_60_days.isoformat()})
    body = client.get("/api/v1/products/", params={"expiration": "vigente"}).json()
    assert body["total"] == 1
    assert body["items"][0]["sku"] == "VIG-001"


def test_expiration_filter_sin_fecha(client):
    client.post("/api/v1/products/", json={"sku": "SIN-001", "name": "Sin fecha"})
    body = client.get("/api/v1/products/", params={"expiration": "sin_fecha"}).json()
    assert body["total"] == 1
    assert body["items"][0]["sku"] == "SIN-001"
    assert body["items"][0]["expiration_status"] == "sin_fecha"


def test_settings_value_used_in_expiration_calculation(client):
    in_40_days = date.today() + timedelta(days=40)
    client.post("/api/v1/products/", json={"sku": "CFG-001", "name": "Configurable", "expiration_date": in_40_days.isoformat()})
    # Con el valor inicial (30 días), 40 días a la fecha sigue "vigente"
    item = client.get("/api/v1/products/", params={"search": "CFG-001"}).json()["items"][0]
    assert item["expiration_status"] == "vigente"
    # Al ampliar el umbral a 45, el cálculo usa el valor guardado
    client.put("/api/v1/settings/", json={"expiration_warning_days": 45})
    item = client.get("/api/v1/products/", params={"search": "CFG-001"}).json()["items"][0]
    assert item["expiration_status"] == "proximo_a_vencer"
    # El filtro de listado también usa el valor guardado
    body = client.get("/api/v1/products/", params={"expiration": "proximo_a_vencer"}).json()
    assert any(p["sku"] == "CFG-001" for p in body["items"])


def test_settings_out_of_range_message(client):
    for value in (999, -1):
        response = client.put("/api/v1/settings/", json={"expiration_warning_days": value})
        assert response.status_code == 422
        messages = [item.get("msg", "") for item in response.json()["detail"]]
        assert any("El valor debe estar entre 0 y 365 días" in msg for msg in messages)
