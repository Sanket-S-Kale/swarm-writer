from tavily import TavilyClient
import wikipedia
import arxiv
from ..config import settings
import asyncio

class ResearchTools:
    def __init__(self):
        self.tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        self._web_limiter = asyncio.Semaphore(5)
        self._wiki_limiter = asyncio.Semaphore(2)
        self._arxiv_limiter = asyncio.Semaphore(2)

    async def web_search(self, query: str):
        async with self._web_limiter:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: self.tavily.search(query=query, search_depth="advanced"))

    async def wiki_search(self, query: str):
        async with self._wiki_limiter:
            loop = asyncio.get_event_loop()
            def _wiki():
                try:
                    return wikipedia.summary(query, sentences=5)
                except:
                    return f"No Wikipedia results found for {query}"
            return await loop.run_in_executor(None, _wiki)

    async def arxiv_search(self, query: str):
        async with self._arxiv_limiter:
            loop = asyncio.get_event_loop()
            def _arxiv():
                search = arxiv.Search(
                    query=query,
                    max_results=5,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                results = []
                for r in search.results():
                    results.append({
                        "title": r.title,
                        "summary": r.summary,
                        "url": r.pdf_url,
                        "authors": [a.name for a in r.authors]
                    })
                return results
            return await loop.run_in_executor(None, _arxiv)
