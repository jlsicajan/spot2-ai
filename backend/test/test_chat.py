from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_missing_fields_triggers_followup():
    payload = {
        "message": "Estoy buscando una oficina en Guadalajara",
        "session_data": {},
    }
    response = client.post("/chat", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert "presupuesto" in data["response"].lower()
    assert isinstance(data["session_data"], dict)


def test_fills_fields_step_by_step():
    session_data = {}
    for step in [
        "Estoy buscando una oficina en Guadalajara",
        "Con un presupuesto de 30000 pesos",
        "Tamaño de 500 metros cuadrados",
        "Sí, es una oficina",
    ]:
        res = client.post("/chat", json={"message": step, "session_data": session_data})
        assert res.status_code == 200
        session_data = res.json()["session_data"]

    assert all(
        k in session_data and session_data[k]
        for k in ["budget", "total_size", "real_estate_type", "city"]
    )


def test_final_message_contains_summary():
    payload = {
        "message": "Necesito una oficina industrial en Monterrey de 600 m2 con un presupuesto de 50000 pesos",
        "session_data": {},
    }
    response = client.post("/chat", json=payload)
    data = response.json()

    assert "Resumen de tu búsqueda" in data["response"]
    assert "oficina industrial" in data["response"].lower()
