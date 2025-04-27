"""
muitliple users
task tracker
create a task
- Title
- Description
- Due Date
- Status
delete a task
update a task
get all tasks

! include unit tests
store data in a database
document api endpoints
validation and error handling
?login screen
"""

from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3
import uvicorn
from auth_handler import hash_password, check_password, authenticate_user, create_access_token, verify_token, require_role


app = FastAPI()

path = "HMCTS\\Backend"

# put websites that can access the api
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Pydantic model for request validation
class Task(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1)
    description: Optional[str] = ""
    due_date: str = Field(..., min_length=1)
    priority: int = 1
    status: str = "pending"

# admin can view all users 
def add_admin_user():
    try:
        conn = sqlite3.connect(path + "\\users.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hash_password("Admin1234!"), "admin"))
        conn.commit()
        conn.close()
    # admin a
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(path + "\\users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    conn.commit()
    conn.close()
    conn = sqlite3.connect(path + "\\task_tracker.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 1,
            due_date TEXT NOT NULL, 
            FOREIGN KEY (user_id) REFERENCES tasks (id)
        )
    ''')
    conn.commit()
    conn.close()
    add_admin_user()

@app.post("/register")
def create_new_user(username:str=Form(...), password:str=Form(...)):
    conn = sqlite3.connect(path + "\\users.db", check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    new_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, new_password))
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    conn.commit()
    conn.close()
    
    return {"message": "User created successfully"}

@app.post("/login")
def login(username:str=Form(...), password:str=Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(user)
    return {"id": user["id"], "username": user["username"], "role": user["role"], "access_token": access_token}  


@app.get("/tasks")
def get_user_tasks(user=Depends(verify_token)):
    user_id = user["id"]
    conn = sqlite3.connect(path + "\\task_tracker.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    if len(tasks) == 0:
        raise HTTPException(status_code=404, detail="No tasks found")
    return [{"id": r[0], "user_id": r[1], "title": r[2], "description": r[3], "status": r[4], "priority": r[5], "due_date": r[6]} for r in tasks]


@app.get("/tasks/{task_id}")
def get_task(task_id:int, user=Depends(verify_token)):
    conn = sqlite3.connect(path + "\\task_tracker.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task[0], "user_id": task[1], "title": task[2], "description": task[3], "status": task[4], "priority": task[5], "due_date": task[6]}

@app.put("/tasks/{task_id}")
def update_task(task_id:int, task:Task, user=Depends(verify_token)):
    conn = sqlite3.connect(path + "\\task_tracker.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ?, description = ?, status = ?, priority = ?, due_date = ? WHERE id = ?", (task.title, task.description, task.status, task.priority, task.due_date, task_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    conn.close()
    return {"message": "Task updated successfully"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id:int, user=Depends(verify_token)):
    conn = sqlite3.connect(path + "\\task_tracker.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.commit()
    finally:
        conn.close()
    return {"message": "Task deleted successfully"}

@app.post("/tasks")
def create_task(task:Task, user=Depends(verify_token)):
    user_id = user["id"]
    conn = sqlite3.connect(path + "\\task_tracker.db", check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, description, status, priority, due_date) VALUES (?, ?, ?, ?, ?, ?)", (user_id, task.title, task.description, task.status, task.priority, task.due_date))
    conn.commit()
    conn.close()
    return {"message": "Task created successfully"}

@app.get("/users")
def get_all_users(user=Depends(require_role("admin"))):
    conn = sqlite3.connect(path + "\\users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return [{"id": r[0], "username": r[1], "role": r[3]} for r in users]


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)