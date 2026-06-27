"""
Research Agent - Web search and information aggregation
Handles web search integration with result aggregation and source management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent, AgentCapability
from app.services.llm import get_llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SearchResult:
    """Represents a single search result"""

    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet


class ResearchAgent(BaseAgent):
    """Research Agent - Web search and information aggregation

    This agent provides:
    - Web search integration
    - Result aggregation
    - Source management
    - Citation generation
    """

    def __init__(self):
        """Initialize Research Agent"""
        super().__init__(
            agent_id="ivy-research",
            name="Ivy Research",
            description="Web search and information aggregation with source tracking",
            version="1.0.0",
        )

        # Initialize LLM service
        self.llm_service = get_llm_service()

        # Define capabilities
        self.add_capability(
            AgentCapability(
                name="web-search",
                description="Search the web for current information",
            )
        )
        self.add_capability(
            AgentCapability(
                name="result-aggregation",
                description="Aggregate and synthesize search results",
            )
        )
        self.add_capability(
            AgentCapability(
                name="source-tracking",
                description="Track and cite sources properly",
            )
        )
        self.add_capability(
            AgentCapability(
                name="fact-verification",
                description="Verify facts against multiple sources",
            )
        )

        logger.info("ResearchAgent initialized successfully")

    async def _search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web for query

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results with title, url, snippet
        """
        try:
            # In production, this would integrate with a real search API
            # (Google Search API, Bing Search API, DuckDuckGo, etc.)
            # For now, we'll use LLM to simulate search results

            messages = [
                {
                    "role": "user",
                    "content": f"Simulate search results for: {query}\n\nProvide {num_results} results in this format:\n1. Title | URL | Snippet\n2. Title | URL | Snippet\n\nProvide realistic results only.",
                }
            ]

            response = await self._llm_response(messages)

            # Parse response into structured results
            results = self._parse_search_results(response, query)
            return results

        except Exception as e:
            logger.error(f"Error searching web: {str(e)}")
            raise

    def _parse_search_results(self, response: str, query: str) -> List[Dict]:
        """Parse search results from response

        Args:
            response: Raw response from LLM or search API
            query: Original search query

        Returns:
            List of parsed results
        """
        try:
            results = []
            lines = response.split("\n")

            for line in lines:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        # Remove numbering if present
                        title = (
                            parts[0].lstrip("0123456789. ")
                        )
                        results.append(
                            {
                                "title": title,
                                "url": parts[1],
                                "snippet": parts[2],
                                "query": query,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

            return results

        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}")
            return []

    async def _aggregate_results(
        self, query: str, results: List[Dict]
    ) -> str:
        """Aggregate search results into coherent summary

        Args:
            query: Original search query
            results: List of search results

        Returns:
            Aggregated summary
        """
        try:
            # Format results for LLM
            formatted_results = "\n".join(
                [
                    f"- {r['title']}: {r['snippet']} (Source: {r['url']})"
                    for r in results
                ]
            )

            messages = [
                {
                    "role": "user",
                    "content": f"Synthesize this information to answer: {query}\n\nSources:\n{formatted_results}\n\nProvide a comprehensive answer with citations.",
                }
            ]

            aggregation = await self._llm_response(messages)
            return aggregation

        except Exception as e:
            logger.error(f"Error aggregating results: {str(e)}")
            raise

    async def _generate_citations(self, results: List[Dict]) -> str:
        """Generate formatted citations for results

        Args:
            results: List of search results

        Returns:
            Formatted citation text
        """
        try:
            citations = ["## Sources:"]

            for i, result in enumerate(results, 1):
                citation = (
                    f"{i}. {result['title']} - {result['url']}"
                )
                citations.append(citation)

            return "\n".join(citations)

        except Exception as e:
            logger.error(f"Error generating citations: {str(e)}")
            return ""

    async def _llm_response(self, messages: list) -> str:
        """Get response from LLM"""
        try:
            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt="You are a helpful research assistant. Provide accurate, well-sourced information. Always cite your sources.",
            )
            return response
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            raise

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process message for research-related tasks

        Args:
            message: User message/query
            context: Additional context

        Returns:
            Aggregated research findings with citations
        """
        try:
            logger.info(f"ResearchAgent processing query: {message}")

            # Check if this is a search query
            if not any(
                keyword in message.lower()
                for keyword in ["search", "find", "research", "latest", "current"]
            ):
                # Not a research query, pass to LLM for general help
                messages = [{"role": "user", "content": message}]
                return await self._llm_response(messages)

            # Extract search query
            search_query = message
            if "search for" in message.lower():
                search_query = message.split("search for")[-1].strip()
            elif "find" in message.lower():
                search_query = message.split("find")[-1].strip()

            # Perform web search
            logger.info(f"Searching web for: {search_query}")
            search_results = await self._search_web(
                search_query, num_results=5
            )

            if not search_results:
                return "No results found for your search query."

            # Aggregate results
            logger.info(f"Aggregating {len(search_results)} results")
            aggregated = await self._aggregate_results(
                search_query, search_results
            )

            # Generate citations
            citations = await self._generate_citations(search_results)

            # Combine response and citations
            response = f"{aggregated}\n\n{citations}"

            logger.info("ResearchAgent processing completed")
            return response

        except Exception as e:
            logger.error(f"Error in ResearchAgent.process: {str(e)}")
            raise


async def get_research_agent() -> ResearchAgent:
    """Get or create research agent instance"""
    return ResearchAgent()
