#STEPS
#1. Health & echo. Add GET /ping returning {"pong": true}, and GET /echo/{word} returning the word reversed.
#2. Typed query. Add GET /tax taking amount: float and rate: float = 0.17; return the tax and total. Confirm a string amount yields 422.
#3. Status codes. Make POST /products return HTTP 201 using status_code=201. Read the response in /docs.
#4. Explore docs. Open /docs and /openapi.json. Find where your parameter types appear in thegenerated schema.




from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="tax")

@app.get("/ping")
def ping():
    return {"pong": True}

@app.get("/echo/{word}")
def echo(word: str):
    return word[::-1] 

@app.get("/tax")
def calculate_tax(amount: float, rate: float = 0.17):
    tax = amount * rate
    total = amount + tax
    return {"tax": tax, "total": total}

class Product(BaseModel):
    name: str
    price: float

@app.post("/products", status_code=201)
def create_product(product: Product):
    return {"message": "Product created", "product": product}
