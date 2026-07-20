#Worked Example — An async call to an external service
#Step 1. Use httpx.AsyncClient inside an async def endpoint.
#Step 2. await the call so the worker is free meanwhile.
#Step 3. Always set a timeout on external calls.


import httpx
from fastapi import FastAPI,HTTPException
app=FastAPI()
@app.get("/quote")
async def quote():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://api.example.com/quote")
            r.raise_for_status()
        return r.json()
    except httpx.HTTPError:
        raise HTTPException(502, "Upstream service unavailable")