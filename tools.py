import wikipedia
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
from datetime import datetime

# Wikipedia rate-limits (HTTP 429) the library's generic default user agent.
wikipedia.set_user_agent("PythonAIAgent/1.0 (LangChain research assistant)")

@tool("save_text_to_file")
def save_tool(data: str, filename: str = "research_output.txt") -> str:
    """Saves structured research data to a text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)

    return f"Data successfully saved to {filename}"

search = DuckDuckGoSearchRun()
api_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=2000)

# A failing lookup is reported back to the model instead of crashing the whole request.
@tool("search")
def search_tool(query: str) -> str:
    """Search the web for information"""
    try:
        return search.run(query)
    except Exception as e:
        return f"Web search is unavailable right now ({type(e).__name__}). Use another tool or answer from what you have."

@tool("wikipedia")
def wiki_tool(query: str) -> str:
    """Look up a topic on Wikipedia. Input should be a search query."""
    try:
        return api_wrapper.run(query)
    except Exception as e:
        return f"Wikipedia is unavailable right now ({type(e).__name__}). Use another tool or answer from what you have."
