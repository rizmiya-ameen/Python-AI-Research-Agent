import os

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

# Comma-separated, in order of preference. Override with GEMINI_MODELS in .env.
MODELS = [
    name.strip()
    for name in os.getenv("GEMINI_MODELS", "gemini-3.8-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.5-flash-lite").split(",")
    if name.strip()
]

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

SYSTEM_PROMPT = """
You are a research assistant that will help generate a research paper.
Answer the user query and use necessary tools.
List the URLs or page titles you relied on as sources.
"""

def build_agent(allow_save: bool = False):
    # Saving writes to the local disk, so it is only offered to the CLI.
    tools = [search_tool, wiki_tool]
    if allow_save:
        tools.append(save_tool)

    # Free-tier quota is counted per model, so fall through to the next one when a model is exhausted or overloaded.
    llm, *fallbacks = [ChatGoogleGenerativeAI(model=name, max_retries=1) for name in MODELS]
    return create_agent(
        model=llm,
        tools=tools,
        middleware=[ModelFallbackMiddleware(*fallbacks)] if fallbacks else [],
        system_prompt=SYSTEM_PROMPT,
        response_format=ResearchResponse,
    )

def run_research(query: str, allow_save: bool = False) -> ResearchResponse:
    agent = build_agent(allow_save=allow_save)
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    response = result["structured_response"]
    # Report the tools that were actually called rather than what the model claims.
    used = []
    for message in result["messages"]:
        for call in getattr(message, "tool_calls", None) or []:
            if call["name"] != ResearchResponse.__name__ and call["name"] not in used:
                used.append(call["name"])
    response.tools_used = used
    return response
