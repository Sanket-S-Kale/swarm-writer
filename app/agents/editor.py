from .base import BaseAgent

class EditorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Editor",
            system_instruction="""You are a professional academic editor with expertise in improving scholarly writing across disciplines. Your task is to refine and elevate the quality of the academic text provided.

## EDITING PROCESS:
1. Analyze structure, argument flow, and coherence.
2. Ensure logical progression with clear transitions.
3. Improve clarity, precision, and conciseness while maintaining academic tone.
4. Strengthen thesis statements and main arguments.
5. Clarify complex concepts with additional explanations or examples.
6. Preserve all citations [1], [2], etc., and maintain the integrity of the References section.

## FORMATTING:
- Use markdown consistently for headings, emphasis, and lists.
- Return only the revised, polished text without meta-commentary."""
        )

    async def critique_and_refine(self, paper: str, iteration: int):
        self.log_step("Editing", f"Refining paper (Iteration {iteration}/3)")
        
        prompt = f"""
        Iteration Number: {iteration}/3
        
        Current Paper Content:
        {paper}
        
        Task:
        1. Critically analyze the current version for academic rigor, source quality, and narrative flow.
        2. Rewrite the paper to be SIGNIFICANTLY better than the current version. 
           - Fix any repetitive language.
           - Strengthen arguments using the provided data.
           - Ensure citations are perfectly integrated.
        3. Rate the NEW version you just wrote on a scale of 1 to 10.
        
        CRITICAL: Your goal is incremental improvement. If the current version is a 7, your rewrite MUST aim for an 8 or 9. Do not regress.
        
        Return your response in this EXACT format:
        <score>YOUR_SCORE_HERE</score>
        <refined_paper>
        YOUR_IMPROVED_MARKDOWN_HERE
        </refined_paper>
        """
        response = await self.chat(prompt)
        
        import re
        score_match = re.search(r'<score>(\d+)</score>', response)
        paper_match = re.search(r'<refined_paper>(.*?)</refined_paper>', response, re.DOTALL)
        
        score = int(score_match.group(1)) if score_match else 0
        refined_paper = paper_match.group(1).strip() if paper_match else paper
        
        return {
            "score": score,
            "refined_paper": refined_paper
        }
