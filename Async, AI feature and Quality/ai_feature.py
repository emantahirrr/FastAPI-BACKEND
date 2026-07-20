#Worked Example — A /summarize endpoint with validated JSON output
#Step 1. Define input and output Pydantic models — the output is your contract, not the model's whim.
#Step 2. Call the model asking explicitly for JSON; set a timeout.
#Step 3. Parse and re-validate; a malformed reply becomes a clean 502, never a 200.



import json, os, httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI,HTTPException
 
# Provider-agnostic: point BASE_URL/API_KEY at any OpenAI-compatible endpoint
BASE_URL = os.environ["LLM_BASE_URL"]      # e.g. https://api.openai.com/v1
API_KEY  = os.environ["LLM_API_KEY"]
MODEL    = os.environ.get("LLM_MODEL", "gpt-4o-mini")
 
class SummarizeIn(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
 
class SummarizeOut(BaseModel):
    summary: str
    bullet_points: list[str]
 
async def call_llm(messages: list[dict]) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": MODEL, "messages": messages,
                  "response_format": {"type": "json_object"}},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    
app=FastAPI() 
@app.post("/ai/summarize", response_model=SummarizeOut)
async def summarize(body: SummarizeIn):
    raw = await call_llm([
        {"role": "system",
         "content": "Return JSON only: {summary: str, bullet_points: [str]}"},
        {"role": "user", "content": body.text},
    ])
    try:
        return SummarizeOut(**json.loads(raw))   # re-validate the model's output
    except Exception:
        raise HTTPException(502, "Model returned malformed output")
