#Steps
#1. Create main.py and declare a FastAPI app.
#2. Add a GET with a typed path parameter and an optional query parameter.
#3. Run with uvicorn main:app --reload and open /docs.






from fastapi import FastAPI
 
app = FastAPI(title="Catalogue API")
 
@app.get("/")
def health():
    return {"status": "ok"}
 
@app.get("/products/{product_id}")
def get_product(product_id: int, currency: str = "USD"):
    # product_id is forced to int -> non-integer paths auto-return 422
    return {"id": product_id, "currency": currency, "price": 19.99}
 
# Try in /docs:  /products/7?currency=PKR
# Try a bad URL: /products/abc  -> 422 with a precise error, zero extra code