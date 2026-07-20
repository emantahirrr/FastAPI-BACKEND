from fastapi import Depends, FastAPI
app=FastAPI()
def pagination(skip: int = 0, limit: int = 20) -> dict:
    return {"skip": max(skip, 0), "limit": min(max(limit, 1), 100)}
 
@app.get("/products")
def list_products(page: dict = (pagination)):
    return {"page": page, "items": []}
 
@app.get("/orders")
def list_orders(page: dict = (pagination)):   # same logic, zero duplication
    return {"page": page, "items": []}