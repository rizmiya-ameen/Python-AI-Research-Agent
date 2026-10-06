from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent import ResearchResponse, run_research

app = FastAPI(title="Research Agent")

INDEX_HTML = Path(__file__).parent / "static" / "index.html"

class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)

@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML.read_text(encoding="utf-8")

@app.post("/api/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    try:
        return run_research(request.query)
    except Exception as e:
        print("Research failed:", repr(e))
        if "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(status_code=429, detail="The Gemini API quota is used up. Please try again later.")
        raise HTTPException(status_code=502, detail="The research agent failed. Please try again.")
