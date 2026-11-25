from fastapi.testclient import TestClient
from app.main import app, products, orders, users

client = TestClient(app)

def setup_function():
    users.clear()
    products.clear()
    orders.clear()

def test_health_probe():
    assert client.get("/health").json() == {"status": "ok"}

def test_register_route_creates_user():
    response = client.post("/users", json={"email": "a@example.com", "password": "pw"})
    assert response.status_code == 201
    assert response.json()["email"] == "a@example.com"

def test_product_route_creates_product():
    response = client.post("/products", json={"name": "Keyboard", "price": 25, "stock": 8})
    assert response.status_code == 201
    assert response.json()["name"] == "Keyboard"

def test_order_rejects_unknown_product():
    response = client.post("/orders", json={"product_id": "missing", "quantity": 1})
    assert response.status_code == 404
