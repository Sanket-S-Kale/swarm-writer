from .base import BaseAgent
import json

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            system_instruction="""You are an expert research planning agent. Your goal is to orchestrate a team of specialized agents (Researcher, Writer, Editor) to produce high-quality, verifiable academic reports.
            
            PLANNING PROTOCOL:
            1. Decompose the research topic into prioritized, logical steps.
            2. Each step must explicitly name the responsible agent (e.g., 'Research agent', 'Writer agent').
            3. Ensure a clear flow: Discovery -> Targeted Deep-Dive -> Synthesis -> Review -> Finalization.
            4. Focus on information density and source verification at every stage."""
        )

    async def plan_research(self, topic: str):
        prompt = f"""
        You are a planning agent responsible for organizing a research workflow using multiple intelligent agents.

        🧠 Available agents:
        - Research agent: MUST begin with a broad **web search using Tavily** to identify only **relevant** and **authoritative** items (e.g., high-impact venues, seminal works, surveys, or recent comprehensive sources). The output of this step MUST capture for each candidate: title, authors, year, venue/source, URL, and (if available) DOI.
        - Research agent: AFTER the Tavily step, perform a **targeted arXiv search** ONLY for the candidates discovered in the web step (match by title/author/DOI). If an arXiv preprint/version exists, record its arXiv URL and version info. Do NOT run a generic arXiv search detached from the Tavily results.
        - Writer agent: drafts based on research findings.
        - Editor agent: reviews, reflects on, and improves drafts.

        🎯 Produce a clear step-by-step research plan as a JSON list of strings (e.g., ["Step 1", "Step 2", ...]).
        Each step must be atomic, actionable, and assigned to one of the agents.
        Maximum of 7 steps.

        🚫 DO NOT include steps like “create CSV”, “set up repo”, “install packages”.
        ✅ Focus on meaningful research tasks (search, extract, rank, draft, revise).
        ✅ The FIRST step MUST be exactly: 
        "Research agent: Use Tavily to perform a broad web search and collect top relevant items (title, authors, year, venue/source, URL, DOI if available)."
        ✅ The SECOND step MUST be exactly:
        "Research agent: For each collected item, search on arXiv to find matching preprints/versions and record arXiv URLs (if they exist)."

        🔚 The FINAL step MUST instruct the writer agent to generate a comprehensive Markdown report that:
        - Uses all findings and outputs from previous steps
        - Includes inline citations (e.g., [1], (Wikipedia/arXiv))
        - Includes a References section with clickable links for all citations
        - Preserves earlier sources
        - Is detailed and self-contained

        Topic: "{topic}"
        """
        self.log_step("Planning", f"Generating instruction-based research plan for: {topic}")
        response = await self.chat(prompt, format_json=True)
        try:
            # We explicitly ask for JSON list now to stay compatible with BaseAgent's format_json
            import json
            return json.loads(response)
        except Exception as e:
            print(f"[{self.name}] Error parsing plan: {e}")
            # Fallback to a basic 3-step plan if LLM fails
            return [
                "Research agent: Use Tavily to perform a broad web search and collect top relevant items (title, authors, year, venue/source, URL, DOI if available).",
                "Research agent: For each collected item, search on arXiv to find matching preprints/versions and record arXiv URLs (if they exist).",
                f"Writer agent: generate a comprehensive Markdown report for {topic} with inline citations and references."
            ]
