import os
from tavily import TavilyClient


def search_web(query: str) -> str:
    """Search the internet for information.

    Args:
        query: The search query.
    """
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing. "
            "Set your API key before searching."
        )

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        search_depth="basic",
        max_results=3
    )

    results = response.get("results", [])

    if not results:
        return "No search results found."

    sources = []

    for i, result in enumerate(results, 1):
        sources.append(
            f"[W{i}] {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Excerpt: {result.get('content', '')[:700]}"
        )

    return "\n\n".join(sources)


if __name__ == "__main__":
    print(search_web(
        "research on age and entrepreneurial success"
    ))
