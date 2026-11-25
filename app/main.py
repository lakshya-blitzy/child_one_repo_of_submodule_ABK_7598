from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import uuid4

app = FastAPI(title="Customer Orders API")
users, products, orders = {}, {}, {}

class RegisterRequest(BaseModel):
    email: str
    password: str

class ProductRequest(BaseModel):
    name: str
    price: float
    stock: int

class OrderRequest(BaseModel):
    product_id: str
    quantity: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/users", status_code=201)
def register(payload: RegisterRequest):
    if payload.email in users:
        raise HTTPException(409, "email already registered")
    user_id = str(uuid4())
    users[payload.email] = {"id": user_id, "password": payload.password}
    return {"id": user_id, "email": payload.email}

@app.post("/login")
def login(payload: RegisterRequest):
    user = users.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(401, "invalid credentials")
    return {"user_id": user["id"], "token": f"token-{user['id']}"}

@app.post("/products", status_code=201)
def create_product(payload: ProductRequest):
    product_id = str(uuid4())
    products[product_id] = payload.model_dump()
    return {"id": product_id, **products[product_id]}

@app.get("/products")
def list_products():
    return [{"id": key, **value} for key, value in products.items()]

@app.post("/orders", status_code=201)
def create_order(payload: OrderRequest):
    product = products.get(payload.product_id)
    if product is None:
        raise HTTPException(404, "product not found")
    if payload.quantity <= 0:
        raise HTTPException(400, "quantity must be positive")
    if product["stock"] < payload.quantity:
        raise HTTPException(409, "insufficient stock")
    product["stock"] -= payload.quantity
    order_id = str(uuid4())
    orders[order_id] = {
        "id": order_id,
        "product_id": payload.product_id,
        "quantity": payload.quantity,
        "total": round(product["price"] * payload.quantity, 2),
    }
    return orders[order_id]

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(404, "order not found")
    return orders[order_id]
