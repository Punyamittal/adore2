from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import datetime

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./tasks.db"  # You might need to adjust this to your actual database URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Task model
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    due_date = Column(DateTime)
    priority = Column(Integer)
    status = Column(String)
    parent_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    duration = Column(Integer)
