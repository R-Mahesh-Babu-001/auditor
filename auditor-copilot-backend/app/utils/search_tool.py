from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper


@tool
def get_search_tool():
    """Returns a web search tool using SerpAPI."""
    search = SerpAPIWrapper()
    # return Tool(
    #     name="web_search",
    #     func=search.run,
    #     description="Search the web for audit-related information"
    # )
    return search


"""
Utility for providing a web search tool (SerpAPI) to agents.
"""

# get_search_tool returns a SerpAPIWrapper instance for web search.

