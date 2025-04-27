import pytest
import sqlite3
import bcrypt
from pydantic import SecretStr
from fastapi import HTTPException
from fastapi.testclient import TestClient
from auth_handler import create_access_token
from main import (
    app,
    Task,
    create_new_user,
    hash_password,
    check_password,
    login,
    init_db,
    get_user_tasks,
    delete_task,
    update_task,
    create_task
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_tasks_table():
    # Clear tasks before and after the test
    yield
    with sqlite3.connect("task_tracker.db") as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()

@pytest.fixture(autouse=True)
def clear_users_table():
    # Clear users before and after the test
    yield
    with sqlite3.connect("users.db") as conn:
        conn.execute("DELETE FROM users")
        conn.commit()

def get_test_token():
    return create_access_token({"id": 1, "username": "test", "role": "user"})

def test_hash_password():
    password = "Valid1234!"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert bcrypt.checkpw(password.encode(), hashed.encode())

def test_hash_password_fail():
    with pytest.raises(HTTPException) as e:
        hash_password("short")
    assert e.value.status_code == 400
    assert e.value.detail == "Password must be at least 10 characters long and contain at least one uppercase letter, one number, and one special character"

def test_check_password():
    password = "StrongPass1!"
    hashed = hash_password(password)
    assert check_password(password, hashed) is True

def test_check_password_fail():
    password = "StrongPass1!"
    wrong_password = "WrongPass2@"
    hashed = hash_password(password)
    assert check_password(wrong_password, hashed) is False

def test_create_new_user(mocker):
    # Setup connection and cursor
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    # mock_conn.execute = mocker.MagicMock()  # ✅ Add this line to mock execute()

    # Patch the connect call and hash_password
    mocker.patch("main.sqlite3.connect", return_value=mock_conn)
    mocker.patch("main.hash_password", return_value="hashed_password")

    # Make the request
    response = client.post("/register", data={"username": "test_user", "password": "Test_password1"})

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

    mock_conn.execute.assert_called_once_with("PRAGMA journal_mode=WAL;")  # ✅ This will now pass
    mock_cursor.execute.assert_any_call(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("test_user", "hashed_password")
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_create_duplicate_user(mocker):
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mocker.patch("main.hash_password", return_value="hashed_password")
    response = client.post("/register", data={"username": "test_user", "password": "Test_password1"})

    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}
    mock_conn.assert_called_once_with("HMCTS\\Backend\\users.db", check_same_thread=False)
    mock_conn.return_value.execute.assert_called_once_with("PRAGMA journal_mode=WAL;")
    mock_cursor.execute.assert_any_call("INSERT INTO users (username, password) VALUES (?, ?)",("test_user", "hashed_password"))
    mock_conn.return_value.commit.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

    mock_cursor.execute.side_effect = sqlite3.IntegrityError
    response = client.post("/register", data={"username": "test_user", "password": "Test_password1"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}

def test_login(mocker):
    # Patch the sqlite3.connect to mock database operations
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    # create a test user
    username = "user"
    password = "Password123!"  # Plain text password for testing
    hashed = hash_password(password)  # Hash the password using the hash_password function
    mock_cursor.fetchone.return_value = (1, username, hashed, "user", "access_token")  # Mock the database response
    mocker.patch("auth_handler.jwt.encode", return_value="access_token")
    # Perform login with plain text password
    response = client.post("/login", data={"username": username, "password": password})

    # Assert the response is successful
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"id": 1, "username": username, "role": "user", "access_token": "access_token"}

    # Ensure the correct database calls were made
    mock_conn.assert_called_once_with("HMCTS\\Backend\\users.db", check_same_thread=False)
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = ?", (username,))
    mock_conn.return_value.close.assert_called_once()

def test_login_fail(mocker):
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    mock_cursor.fetchone.return_value = None
    with pytest.raises(HTTPException) as exc:
        login("test_user", "test_password")
        mock_conn.assert_called_once_with("users.db", check_same_thread=False)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = ?", ("test_user",))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid username or password"

def test_login_incorrect_password(mocker):
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    username = "user"
    password = "Password123!"  # Plain text password for testing
    hashed = hash_password(password)  # Hash the password using the hash_password function
    mock_cursor.fetchone.return_value = (1, username, hashed)  # Mock the database response

    with pytest.raises(HTTPException) as exc:
        login("test_user1", "Test_password1")
        mock_conn.assert_called_once_with("users.db", check_same_thread=False)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = ?", ("test_user",))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid username or password"
    mock_conn.return_value.close.assert_called_once()
    
def test_get_user_tasks(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (1,1, "Test Task 1", "This is a test task", "pending", 2, "2025-05-01"),
        (1,1, "Test Task 2", "Another test task", "completed", 1, "2025-06-01"),
    ]
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Test Task 1"
    assert data[0]["description"] == "This is a test task"
    assert data[1]["due_date"] == "2025-06-01"
    assert data[1]["status"] == "completed"

    mock_conn.assert_any_call("HMCTS\\Backend\\task_tracker.db", check_same_thread=False)
    print(mock_cursor.execute.call_args_list)
    mock_cursor.execute.assert_any_call("SELECT * FROM tasks WHERE user_id = ?", (1,))
    mock_conn.return_value.close.assert_called_once()

def test_get_user_tasks_logged_out(mocker):
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_user_tasks_empty(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = []
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "No tasks found"

def test_get_user_task(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 1, "Test Task 1", "This is a test task", "pending", 2, "2025-05-01")
    response = client.get("/tasks/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "user_id": 1, "title": "Test Task 1", "description": "This is a test task", "status": "pending", "priority": 2, "due_date": "2025-05-01"}

    mock_conn.assert_called_once_with("HMCTS\\Backend\\task_tracker.db", check_same_thread=False)
    mock_cursor.execute.assert_called_once_with("SELECT * FROM tasks WHERE id = ?", (1,))
    mock_conn.return_value.close.assert_called_once()

def test_get_user_task_not_found(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None
    response = client.get("/tasks/1", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

    mock_conn.assert_called_once_with("HMCTS\\Backend\\task_tracker.db", check_same_thread=False)
    mock_cursor.execute.assert_called_once_with("SELECT * FROM tasks WHERE id = ?", (1,))
    mock_conn.return_value.close.assert_called_once()

def test_get_user_task_logged_out(mocker):
    response = client.get("/tasks/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_task_logged_out(mocker):
    response = client.delete("/tasks/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_task(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    
    mock_cursor.fetchone.return_value = (1, "Test Task 1", "This is a test task", "pending", 2, "2025-05-01")
    response = client.delete("/tasks/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}

    mock_conn.assert_called_once_with("HMCTS\\Backend\\task_tracker.db", check_same_thread=False)
    mock_cursor.execute.assert_called_once_with("DELETE FROM tasks WHERE id = ?", (1,))
    mock_conn.return_value.commit.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_update_task_logged_out(mocker):    
    task = Task(
        user_id=1,
        title="Test Task",
        description="Test Desc",
        status="in progress",
        priority=1,
        due_date="2025-05-01"
    )
    response = client.put("/tasks/1", json=task.model_dump())
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_task(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value

    task_data = {
        "user_id": 1,
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2025-04-30",
        "priority": 1,
        "status": "in progress"
    }

    response = client.put("/tasks/1", json=task_data, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Task updated successfully"}
    mock_cursor.execute.assert_called_once()

def test_update_task_fail(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    mock_cursor.rowcount = 0  # Simulate no task updated

    task_data = {
        "user_id": 999,  # Non-existent ID
        "title": "Non-existent Task",
        "description": "Should fail",
        "due_date": "2025-04-30",
        "priority": 1,
        "status": "pending"
    }

    response = client.put("/tasks/999", json=task_data, headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_create_task_logged_out(mocker):
    task = Task(
        user_id=1,
        title="Test Task",
        description="Test Desc",
        status="in progress",
        priority=1,
        due_date="2025-05-01"
    )
    response = client.post("/tasks", json=task.model_dump())
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_task_empty_title(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    task = {
        "user_id":1,
        "title":"",
        "description":"Test Desc",
        "status":"in progress",
        "priority":1,
        "due_date":"12/20/2023"
    }
    response = client.post("/tasks", json=task, headers=headers)
    assert response.status_code == 422
    # assert response.json()["detail"] == "Title cannot be empty"

def test_create_task_empty_due_date(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    task = {
        "user_id":1,
        "title":"Test Title",
        "description":"Test Desc",
        "status":"in progress",
        "priority":1,
        "due_date":""
    }
    response = client.post("/tasks", json=task, headers=headers)
    assert response.status_code == 422
    # assert response.json()["detail"] == "Due date cannot be empty"

def test_create_task(mocker):
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    mock_conn = mocker.patch("main.sqlite3.connect")
    mock_cursor = mock_conn.return_value.cursor.return_value
    task = Task(
        user_id=1,
        title="Test Title",
        description="Test Desc",
        status="in progress",
        priority=1,
        due_date="2025-1-1"
    )

    response = client.post("/tasks", json=task.model_dump(), headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message" : "Task created successfully"}
    mock_conn.assert_called_once_with("HMCTS\\Backend\\task_tracker.db", check_same_thread=False)
    mock_cursor.execute.assert_called_once()
    mock_conn.return_value.commit.assert_called_once()
    mock_cursor.execute.assert_called_once_with("INSERT INTO tasks (user_id, title, description, status, priority, due_date) VALUES (?, ?, ?, ?, ?, ?)", (task.user_id, task.title, task.description, task.status, task.priority, task.due_date))
    mock_conn.return_value.close.assert_called_once()
