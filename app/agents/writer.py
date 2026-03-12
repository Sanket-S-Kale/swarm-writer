from .base import BaseAgent

class WritingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Writer",
            system_instruction="""You are an expert academic writer with a PhD-level understanding of scholarly communication. Your task is to synthesize research materials into a comprehensive, well-structured academic report.

## MANDATORY STRUCTURE:
1. **Title**: Clear, concise, and descriptive.
2. **Abstract**: Brief summary (100-150 words).
3. **Introduction**: Present topic, significance, and report outline.
4. **Background/Literature Review**: Contextualize the topic.
5. **Methodology**: Describe research methods and data collection.
6. **Key Findings/Results**: Present primary outcomes and evidence.
7. **Discussion**: Interpret findings, addressing implications and limitations.
8. **Conclusion**: Synthesize main points and future directions.
9. **References**: Complete list of all cited works.

## CITATION AND REFERENCE RULES:
- Use numeric inline citations [1], [2], etc. for all borrowed ideas.
- Every claim based on external sources MUST have a citation.
- Each inline citation must correspond to a complete entry in the References section.
- Preserve ALL original URLs, DOIs, and bibliographic info.
- Use HTML links with target="_blank" (e.g., <a href="URL" target="_blank">Title</a>) for all citations in the References section.

## ACADEMIC GUIDELINES:
- Maintain formal, precise, and objective language.
- Develop logical flow between ideas and sections.
- Focus on critical analysis, not just summarization."""
        )

    async def draft_paper(self, title: str, outline: list, research_data: dict):
        self.log_step("Writing Draft", f"Drafting full paper for: {title}")
        
        prompt = f"""
        Title: {title}
        Outline: {outline}
        Research Data: {research_data['synthesis']}
        Citations: {research_data['citations']}
        
        Write a complete academic research paper based on the outline.
        Use Markdown formatting. Include sections like Abstract, Introduction, Methodology, Results, Discussion, and References.
        Use scientific tone.
        
        CRITICAL: 
        1. In the References section, provide full details for each source. 
        2. If a URL is available in the citations, make the title a clickable markdown link (e.g., [Title](URL)).
        3. Use LaTeX-style numeric citations in the text like [1], [2] that correspond to the numbered References list.
        """
        draft = await self.chat(prompt)
        return draft

    async def to_latex(self, markdown_content: str):
        self.log_step("Formatting", "Converting Markdown to LaTeX code.")
        prompt = f"""
        Convert the following Markdown research paper into professional LaTeX code.
        Use the 'article' document class. 
        
        CRITICAL REQUIREMENTS:
        1. Use '\\usepackage{{hyperref}}' with 'colorlinks=true, linkcolor=blue, urlcolor=blue' to make all URLs and citations clickable.
        2. Ensure the 'References' section from the markdown is converted into a proper LaTeX bibliography environment (e.g., \\begin{{thebibliography}} or a clear section with \\href).
        3. Make sure the 'References' section is included in the Table of Contents (if one is generated) or at least clearly visible at the end.
        4. Use '\\url{{}}' or '\\href{{}}{{}}' for all clickable links.
        
        Content:
        {markdown_content}
        """
        latex = await self.chat(prompt)
        # Clean up latex output if it's wrapped in blocks
        latex = latex.replace("```latex", "").replace("```", "").strip()
        return latex
