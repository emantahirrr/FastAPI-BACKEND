#steps
#1. Write pagination() returning a clamped skip/limit dict.
#2. Inject it with Depends into a list endpoint.
#3. Reuse the same dependency in a second endpoint without copy-paste.





from fastapi import FastAPI, Depends
app= FastAPI()
def pagination(skip: int=0, limit: int=20)-> dict:
    return{"skip": max(skip,0), "limit":min(max(limit,1),100)}
@app.get("/products")
def list_products(page :dict = Depends(pagination)):
    return{"page":page, "items":[]}
@app.get("/orders")
def list_orders(page:dict =Depends(pagination)):
    return{"page":page, "items":[]}
