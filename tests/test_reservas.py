# tests/test_reserva.py
def test_reserva_sin_login(client):
    response = client.post("/reserva/1", data={
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-01-05",
        "pasajeros": 2,
        "precio_total": 2000.00
    }, follow_redirects=False)

    # La reserva sin login debe redirigir a /login
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
