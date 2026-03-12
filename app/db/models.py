from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from ..config import settings

Base = declarative_base()

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    final_paper_md = Column(Text, nullable=True)
    final_paper_latex = Column(Text, nullable=True)
    
    steps = relationship("AgentStep", back_populates="session")

class AgentStep(Base):
    __tablename__ = "agent_steps"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("research_sessions.id"))
    agent_name = Column(String)
    action = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="steps")

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
