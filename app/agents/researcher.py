from .base import BaseAgent
from ..tools.research_tools import ResearchTools
import asyncio

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Researcher",
            system_instruction="""You are an advanced research assistant with expertise in information retrieval and academic research methodology. Your mission is to gather comprehensive, accurate, and relevant information.

## RESEARCH METHODOLOGY:
1. **Analyze Request**: Identify the core research questions and knowledge domains.
2. **Plan Search Strategy**: Determine which tools (Tavily for web, ArXiv for science, Wikipedia for background) are most appropriate.
3. **Execute Searches**: Use the selected tools with effective keywords.
4. **Evaluate Sources**: Prioritize credibility, relevance, recency, and diversity.
5. **Synthesize Findings**: Organize information logically with clear source attribution.

## TOOL GUIDELINES:
- **ArXiv**: Use for peer-reviewed research in CS, Math, Physics, Stats, Bio, Finance, Econ.
- **Tavily**: Use for recent news, industry reports, and diverse web perspectives.
- **Wikipedia**: Use for foundational overviews and historical context.

## OUTPUT REQUIREMENTS:
- **Key Findings**: Organized by subtopic.
- **Source Details**: Include URLs, titles, authors, and publication dates.
- **Limitations**: Note any gaps in available information."""
        )
        self.tools = ResearchTools()

    async def execute_step(self, topic: str, instruction: str, context: dict = None):
        self.log_step("Research Action", f"Executing: {instruction[:100]}...")
        
        # Determine specific action from instruction
        if "Tavily" in instruction and "broad web search" in instruction:
            # Step 1: Broad Web Search
            raw_results = await self.tools.web_search(topic)
            
            # Extract items as structured data
            extraction_prompt = f"""
            Identify authoritative research items (papers, seminal works, surveys) from these results for the topic: {topic}.
            Results: {raw_results}
            
            Return a JSON list of objects:
            [
              {{"title": "...", "authors": "...", "year": "...", "venue": "...", "url": "...", "doi": "..."}}
            ]
            """
            extracted_json = await self.chat(extraction_prompt, format_json=True)
            try:
                import json
                return {"items": json.loads(extracted_json)}
            except:
                return {"items": []}

        elif "arXiv" in instruction and "matching preprints" in instruction:
            # Step 2: Targeted arXiv Search
            items = context.get("items", []) if context else []
            updated_items = []
            
            for item in items[:10]: # Limit to top 10 for performance
                query = f'ti:"{item["title"]}"'
                arxiv_res = await self.tools.arxiv_search(query)
                if arxiv_res:
                    # Found a match
                    item["arxiv_url"] = arxiv_res[0]["url"]
                    item["arxiv_version"] = "v1" # Simplified
                updated_items.append(item)
            
            return {"items": updated_items}

        else:
            # General Research Step
            prompt = f"""
            Topic: {topic}
            Context: {context}
            Instruction: {instruction}
            
            Perform the requested research and provide a summary of your findings.
            """
            synthesis = await self.chat(prompt)
            return {"synthesis": synthesis}
