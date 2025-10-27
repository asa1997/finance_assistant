from fastapi import FastAPI
from pydantic import BaseModel
from .agent import get_agent_response

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/query/")
async def query(query: Query):
    response = get_agent_response(query.text)
    return {"response": response}
