#Worked Example — The four-step RAG loop
#Step 1. Embed the incoming question into a vector.
#Step 2. Retrieve the k nearest stored chunks.
#Step 3. Build a context string and ask the model to answer using only that context.
#Step 4. Return the answer plus the source ids so the answer is auditable.


@app.post("/ai/ask")
async def ask(question: str, session: Session = Depends(get_session)):
    q_vec  = await embed(question)                    # 1. embed query
    chunks = nearest_chunks(session, q_vec, k=4)      # 2. retrieve top-k
    context = "\n\n".join(c.text for c in chunks)    # 3. build context
    answer = await call_llm([
        {"role": "system",
         "content": "Answer ONLY from the context. If unknown, say so."},
        {"role": "user", "content": f"Context:\n{context}\n\nQ: {question}"},
    ])
    return {"answer": answer, "sources": [c.id for c in chunks]}   # 4. cite