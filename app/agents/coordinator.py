from .planner import PlanningAgent
from .researcher import ResearchAgent
from .writer import WritingAgent
from .editor import EditorAgent
from ..db.models import SessionLocal, ResearchSession, AgentStep
import asyncio

class ResearchCoordinator:
    def __init__(self, websocket_manager=None):
        self.planner = PlanningAgent()
        self.researcher = ResearchAgent()
        self.writer = WritingAgent()
        self.editor = EditorAgent()
        self.wss = websocket_manager

    async def broadcast(self, session_id, agent, action, content):
        try:
            # Save to DB
            db = SessionLocal()
            step = AgentStep(session_id=session_id, agent_name=agent, action=action, content=content)
            db.add(step)
            db.commit()
            db.close()
        except Exception as e:
            print(f"DB Log Error: {e}")
        
        try:
            # Broadcast via WebSocket if available
            if self.wss:
                await self.wss.broadcast({
                    "session_id": session_id,
                    "agent": agent,
                    "action": action,
                    "content": content
                })
        except Exception as e:
            print(f"WS Broadcast Error: {e}")

    async def run_workflow(self, topic: str):
        session_id = None
        try:
            # Initialize session
            db = SessionLocal()
            session = ResearchSession(topic=topic)
            db.add(session)
            db.commit()
            session_id = session.id
            db.close()

            await self.broadcast(session_id, "System", "Initialization", "Research session started and persistence initialized.")

            # Step 1: Plan
            await self.broadcast(session_id, "Planner", "Planning", "Reasoning about research workflow...")
            steps = await self.planner.plan_research(topic)
            await self.broadcast(session_id, "Planner", "Plan Created", f"Orchestrating {len(steps)} atomic steps.")
            
            # Context to be shared between agents
            context = {"steps": steps}
            current_paper = ""
            
            # Iterative execution of steps
            for i, step in enumerate(steps):
                agent_type = "System"
                if "Research agent" in step: agent_type = "Researcher"
                elif "Writer agent" in step: agent_type = "Writer"
                elif "Editor agent" in step: agent_type = "Editor"
                
                await self.broadcast(session_id, agent_type, f"Step {i+1}/{len(steps)}", step)
                
                # Dispatch to agent
                if agent_type == "Researcher":
                    res = await self.researcher.execute_step(topic, step, context)
                    context.update(res)
                elif agent_type == "Writer":
                    # Handle drafting or report generation
                    if i == len(steps) - 1: # Final step usually
                        report_prompt = f"""
                        Topic: {topic}
                        Instructions: {step}
                        Research Data Collected: {context.get('items', [])}
                        Synthesized Context: {context.get('synthesis', '')}
                        """
                        current_paper = await self.writer.chat(report_prompt)
                    else:
                        draft_prompt = f"Step: {step}\nContext: {context}\nTopic: {topic}\nDraft a section of the paper."
                        current_paper = await self.writer.chat(draft_prompt)
                elif agent_type == "Editor":
                    res = await self.editor.critique_and_refine(current_paper, i)
                    current_paper = res.get("refined_paper", current_paper)
                    context["score"] = res.get("score")

            # Finalize: LaTeX Conversion
            await self.broadcast(session_id, "Writer", "Formatting", "Generating final LaTeX academic document...")
            latex_code = await self.writer.to_latex(current_paper)
            await self.broadcast(session_id, "System", "Complete", "Research session finished.")

            # Update Session with final results
            db = SessionLocal()
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            session.final_paper_md = current_paper
            session.final_paper_latex = latex_code
            db.commit()
            db.close()

            return session_id
            
        except Exception as e:
            if session_id:
                await self.broadcast(session_id, "System", "Error", f"Workflow failed: {str(e)}")
            print(f"Workflow Error: {e}")
            raise e
