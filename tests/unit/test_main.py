import pytest
from fastapi import HTTPException
from app.main import (
    health, register, login, create_product, list_products, create_order, get_order,
    RegisterRequest, ProductRequest, OrderRequest, users, products, orders,
)

def setup_function():
    users.clear()
    products.clear()
    orders.clear()

def _register_user(email="a@example.com", password="pw"):
    return register(RegisterRequest(email=email, password=password))

def _create_product(name="Keyboard", price=25.0, stock=8):
    return create_product(ProductRequest(name=name, price=price, stock=stock))

def test_create_order_decrements_stock_and_computes_total():
    product = _create_product(price=25.5, stock=3)
    result = create_order(OrderRequest(product_id=product["id"], quantity=2))
    assert result["total"] == 51.0
    assert result["quantity"] == 2
    assert result["product_id"] == product["id"]
    assert orders[result["id"]] == result
    assert products[product["id"]]["stock"] == 1
    half_cent_product = _create_product(price=10.005, stock=1)
    half_cent_order = create_order(OrderRequest(product_id=half_cent_product["id"], quantity=1))
    assert half_cent_order["total"] == 10.01

def test_create_order_allows_full_stock_depletion():
    product = _create_product(price=25.0, stock=4)
    result = create_order(OrderRequest(product_id=product["id"], quantity=4))
    assert orders[result["id"]] == result
    assert result["total"] == 100.0
    assert products[product["id"]]["stock"] == 0

def test_create_order_rejects_quantity_above_stock():
    product = _create_product(price=25.0, stock=4)
    with pytest.raises(HTTPException) as excinfo:
        create_order(OrderRequest(product_id=product["id"], quantity=5))
    assert excinfo.value.status_code == 409
    assert excinfo.value.detail == "insufficient stock"
    assert products[product["id"]]["stock"] == 4
    assert orders == {}

def test_create_order_rejects_non_positive_quantity():
    product = _create_product(price=25.0, stock=4)
    for quantity in (0, -1):
        with pytest.raises(HTTPException) as excinfo:
            create_order(OrderRequest(product_id=product["id"], quantity=quantity))
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "quantity must be positive"
    assert products[product["id"]]["stock"] == 4
    assert orders == {}

def test_create_order_rejects_unknown_product():
    with pytest.raises(HTTPException) as excinfo:
        create_order(OrderRequest(product_id="missing", quantity=0))
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "product not found"
    assert orders == {}

def test_register_creates_user_without_returning_password():
    result = _register_user()
    assert result["email"] == "a@example.com"
    assert result["id"] == users["a@example.com"]["id"]
    assert "password" not in result

def test_register_rejects_duplicate_email():
    _register_user()
    with pytest.raises(HTTPException) as excinfo:
        register(RegisterRequest(email="a@example.com", password="pw"))
    assert excinfo.value.status_code == 409
    assert excinfo.value.detail == "email already registered"
    assert len(users) == 1

def test_login_returns_user_id_and_token():
    _register_user()
    user_id = users["a@example.com"]["id"]
    assert login(RegisterRequest(email="a@example.com", password="pw")) == {
        "user_id": user_id,
        "token": f"token-{user_id}",
    }

def test_login_rejects_unknown_email():
    with pytest.raises(HTTPException) as excinfo:
        login(RegisterRequest(email="nobody@example.com", password="pw"))
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "invalid credentials"

def test_login_rejects_wrong_password():
    _register_user()
    with pytest.raises(HTTPException) as excinfo:
        login(RegisterRequest(email="a@example.com", password="wrong"))
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "invalid credentials"

def test_get_order_returns_created_order():
    product = _create_product()
    order = create_order(OrderRequest(product_id=product["id"], quantity=2))
    assert get_order(order["id"]) == {
        "id": order["id"],
        "product_id": product["id"],
        "quantity": 2,
        "total": 50.0,
    }

def test_get_order_rejects_unknown_order():
    with pytest.raises(HTTPException) as excinfo:
        get_order("missing")
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "order not found"

def test_create_product_persists_submitted_values():
    result = _create_product()
    assert result["name"] == "Keyboard"
    assert result["price"] == 25.0
    assert result["stock"] == 8
    assert products[result["id"]] == {"name": "Keyboard", "price": 25.0, "stock": 8}

def test_list_products_returns_products_in_insertion_order():
    first = _create_product()
    second = _create_product(name="Mouse", price=15.5, stock=2)
    result = list_products()
    assert result == [
        {"id": first["id"], "name": "Keyboard", "price": 25.0, "stock": 8},
        {"id": second["id"], "name": "Mouse", "price": 15.5, "stock": 2},
    ]

def test_list_products_returns_empty_list_for_empty_store():
    assert list_products() == []

def test_health_returns_ok():
    assert health() == {"status": "ok"}
