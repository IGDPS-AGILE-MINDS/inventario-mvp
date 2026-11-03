def test_cors_allows_configured_local_frontend_and_rejects_other_origins(client):
    allowed = client.options("/api/v1/products/", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    })
    blocked = client.options("/api/v1/products/", headers={
        "Origin": "https://not-allowed.example",
        "Access-Control-Request-Method": "GET",
    })
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in blocked.headers
