# Import FastAPI and dependencies
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from models import Base, Task, engine, SessionLocal
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from task_logic import *

# Initialize the FastAPI app
app = FastAPI(title="StoteWise Backend Assignment",
    description="Good luck with the assignment! :)",
    version="1.0.0",
    contact={
        "name": "Achal Agarwal",
        "email": "achalagarwal.01@gmail.com ",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    })



# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Basic Endpoints

# 1. Retrieve all tasks
@app.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    if tasks is None:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks

# 2. Create a new task


# Define a Pydantic model for task creation
class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: str  # Expecting a string in ISO 8601 format
    priority: int = 1
    status: str = "pending"
    parent_id: Optional[int] = None
    duration: int = 0

@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Convert due_date from string to datetime object
    due_date = datetime.fromisoformat(task.due_date)
    
    db_task = Task(
        name=task.name,
        description=task.description,
        due_date=due_date,
        priority=task.priority,
        status=task.status,
        parent_id=task.parent_id,
        duration=task.duration,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# 3. Delete a task by its task_id
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}


# Level 1 


# Question 2
@app.get("/tasks/question2")
def question2_route(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return question2(tasks)

# Question 3
@app.get("/tasks/question3")
def question3_route(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return question3(tasks)

# Question 4
@app.get("/tasks/question4")
def question4_route(db: Session = Depends(get_db)):
    # Tasks that have no other task pointing to them as parent (no subtasks).
    Child = aliased(Task)
    rows = (
        db.query(Task)
        .outerjoin(Child, Child.parent_id == Task.id)
        .filter(Child.id.is_(None))
        .all()
    )
    return jsonable_encoder(rows)

# Question 5
@app.get("/tasks/question5/{task_id}")
def question5_route(task_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return question5(tasks, task_id)



# Level 2

# Question 6
@app.get("/tasks/question6/{query}")
def question6_route(query: str, db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return question6(tasks, query)

# Question 7
@app.get("/tasks/question7")
def question7_route(
    task_id_a: int = Query(..., description="First task id"),
    task_id_b: int = Query(..., description="Second task id"),
    db: Session = Depends(get_db),
):
    tasks = db.query(Task).all()
    return question7(tasks, task_id_a, task_id_b)

# Question 8
@app.get("/tasks/question8")
def question8_route(
    sort_by: str = Query("created_at", description="Task column to sort by"),
    sort_desc: bool = Query(False, description="Sort descending when true"),
    db: Session = Depends(get_db),
):
    # Created between 26 Aug 2024 and 9 Sep 2024 (inclusive, end of day).
    # Exclude completed tasks (case-insensitive) and tasks created on Sunday (SQLite %w: 0 = Sunday).
    start = datetime(2024, 8, 26)
    end = datetime(2024, 9, 9, 23, 59, 59)
    allowed_sort = {"created_at", "due_date", "priority", "name", "id", "status"}
    order_col = getattr(Task, sort_by) if sort_by in allowed_sort else Task.created_at
    order = order_col.desc() if sort_desc else order_col.asc()
    q = (
        db.query(Task)
        .filter(Task.created_at >= start)
        .filter(Task.created_at <= end)
        .filter(func.lower(Task.status) != "completed")
        .filter(func.strftime("%w", Task.created_at) != "0")
        .order_by(order)
    )
    return jsonable_encoder(q.all())

# Question 9
@app.post("/tasks/question9/{worker_threads}")
def question9_route(worker_threads: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return question9(tasks, worker_threads)


# Default route
@app.get("/")
def default_route():
    return {"message": "Welcome to the Storewise Backend Assignment!", "documentation": "Visit localhost:8000/docs"}
