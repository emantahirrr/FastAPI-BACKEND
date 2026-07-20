#Exercises 
#1. Async fetch. Build an async endpoint that calls a public API with httpx.AsyncClient and a timeout; map upstream failure to 502.
#2. AI summarize. Implement /ai/summarize with input/output models and JSON re-validation. Test the malformed-output path with a mock.
#3. RAG shape. Stub embed and nearest_chunks with fakes and assert /ai/ask returns an answer plus a non-empty sources list.
#4. Test suite. Write three pytest tests: a happy create, a 404, and a 401 on a protected route. Run pytest-q.

import json
from typing import List
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field, ValidationError
import httpx
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import pytest

app = FastAPI(title="async app")

@app.get("/external/fetch")
async def fetch_external_data():
    url = "https://httpbin.org/delay/1"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=2.0)
            response.raise_for_status()
            return response.json()
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Upstream provider failed or timed out: {str(exc)}"
            )
class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to summarize")

class SummaryResponse(BaseModel):
    summary: str
    key_points: List[str]

async def call_llm_api(prompt: str) -> str:
    return json.dumps({
        "summary": "FastAPI is a modern web framework.",
        "key_points": ["Fast performance", "Easy to learn"]
    })

@app.post("/ai/summarize", response_model=SummaryResponse)
async def summarize_text(payload: SummaryRequest):
    prompt = f"Summarize this text: {payload.text}"
    raw_llm_output = await call_llm_api(prompt)
    
    try:
        structured_data = json.loads(raw_llm_output)
        return SummaryResponse(**structured_data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM output failed structural validation: {str(exc)}"
        )

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]
async def fake_embed(text: str) -> List[float]:
    return [0.15, 0.44, -0.92]

async def fake_nearest_chunks(vector: List[float]) -> List[str]:
    return ["FastAPI has natively built-in support for asynchronous code execution."]

@app.post("/ai/ask", response_model=AskResponse)
async def ask_rag(payload: AskRequest):
    vector = await fake_embed(payload.question)
    chunks = await fake_nearest_chunks(vector)
    
    answer = f"The answer to '{payload.question}' relies on async execution."
    return AskResponse(answer=answer, sources=chunks)
def verify_token(authorization: str = Header(...)):
    if authorization != "Bearer secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return authorization

@app.post("/protected/action")
async def protected_endpoint(token: str = Depends(verify_token)):
    return {"status": "success", "message": "Authorized"}

client = TestClient(app)

def test_happy_create_endpoint():
    payload = {"text": "FastAPI is built on top of Starlette and Pydantic."}
    response = client.post("/ai/summarize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["key_points"]) > 0

def test_404_not_found():
    response = client.get("/invalid-route-path")
    assert response.status_code == 404

def test_401_on_protected_route():
    response = client.post("/protected/action", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401

def test_rag_ask_returns_answer_and_sources():
    response = client.post("/ai/ask", json={"question": "Tell me about async"})
    assert response.status_code == 200
    
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0  # Assert sources are not empty

@patch("app.call_llm_api", new_callable=AsyncMock)
async def test_summarize_malformed_output_raises_500(mock_llm):
    # Force the simulated LLM API to return invalid syntax
    mock_llm.return_value = "{'malformed_json_here': "
    
    with patch("app.call_llm_api", mock_llm):
        response = client.post("/ai/summarize", json={"text": "Let's validate this breaks."})
        
    assert response.status_code == 500
    assert "LLM output failed structural validation" in response.json()["detail"]