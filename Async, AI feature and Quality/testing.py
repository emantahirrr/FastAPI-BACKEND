#Worked Example — A fast, deterministic endpoint test
#Step 1. Use TestClient to call endpoints without a live server.
#Step 2. Assert status codes and body shape.
#Step 3. Mock external/LLM calls so tests don't hit the network.



from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
def test_create_hero():
    r = client.post("/heroes", json={"name": "Nova", "power": "flight"})
    assert r.status_code == 201
    assert r.json()["name"] == "Nova"
 
def test_summarize_handles_bad_model(monkeypatch):
    async def fake(_messages): return "not-json"
    monkeypatch.setattr("main.call_llm", fake)
    r = client.post("/ai/summarize", json={"text": "hello"})
    assert r.status_code == 502        # malformed output -> clean error, not crash