from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_dashboard_home() -> None:
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert "Estúdio do Criador - Radar Semanal" in response.text


def test_content_ideas() -> None:
    response = client.get("/dashboard/laboratorio")
    assert response.status_code == 200
    assert "Laboratório" in response.text or "Estúdio do Criador" in response.text


def test_saved_products() -> None:
    response = client.get("/dashboard/garagem")
    assert response.status_code == 200
    assert "Garagem" in response.text or "Estúdio do Criador" in response.text


def test_product_detail() -> None:
    response = client.get("/dashboard/raio-x")
    assert response.status_code == 200
    assert "Raio-X" in response.text or "Estúdio do Criador" in response.text
