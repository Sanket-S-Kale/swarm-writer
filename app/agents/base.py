import google.generativeai as genai
from ..config import settings
import json
import asyncio

class BaseAgent:
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=system_instruction
        )
        self.logs = []

    # Global semaphore to rate limit Gemini API calls (Strictly 1 at a time for free tier)
    _rate_limiter = asyncio.Semaphore(1)

    async def chat(self, prompt: str, format_json: bool = False) -> str:
        async with self._rate_limiter:
            print(f"[{self.name}] Calling Gemini API...")
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
                
                text = response.text
                if format_json:
                    # Robust JSON extraction
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                    if json_match:
                        text = json_match.group(1)
                    else:
                        # Fallback: check if the whole text is JSON but just doesn't have blocks
                        text = text.replace("```json", "").replace("```", "").strip()
                
                # Delay to respect free tier Per-Minute-Limit (RPM)
                await asyncio.sleep(2)
                return text
            except Exception as e:
                print(f"[{self.name}] Gemini API Error: {e}")
                raise e

    def log_step(self, action: str, content: str):
        self.logs.append({
            "agent": self.name,
            "action": action,
            "content": content
        })
        # Note: Broadcaster will pick this up via WebSockets later
