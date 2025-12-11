from fastapi import HTTPException


def test_get_task_detail_success(client, mock_task_service):
    """Test getting task detail."""
    mock_task_service.get_task_detail.return_value = {
        "id": 1,
        "title": "Test Task",
        "description": "Task Description",
        "status": "todo",
        "priority": 2,
        "project_id": 1,
        "sprint_id": 1,
        "parent_id": None,
        "assigned_to": 1,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    response = client.get("/tasks/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Task"
    assert data["status"] == "todo"


def test_get_task_not_found(client, mock_task_service):
    """Test getting non-existent task."""
    mock_task_service.get_task_detail.side_effect = HTTPException(
        status_code=404, detail="Task not found"
    )

    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_get_task_forbidden(client, mock_task_service):
    """Test getting task from project user is not member of."""
    mock_task_service.get_task_detail.side_effect = HTTPException(
        status_code=403, detail="You are not a member of this project"
    )

    response = client.get("/tasks/1")

    assert response.status_code == 403


def test_update_task_success(client, mock_task_service):
    """Test updating a task."""
    mock_task_service.update_task.return_value = {
        "id": 1,
        "title": "Updated Task",
        "description": "Updated Description",
        "status": "in_progress",
        "priority": 1,
        "project_id": 1,
        "sprint_id": 1,
        "parent_id": None,
        "assigned_to": 2,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T01:00:00",
    }

    payload = {
        "title": "Updated Task",
        "status": "in_progress",
        "priority": 1,
        "assigned_to": 2,
    }

    response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["status"] == "in_progress"
    assert data["priority"] == 1


def test_update_task_mark_as_done(client, mock_task_service):
    """Test marking task as done."""
    mock_task_service.update_task.return_value = {
        "id": 1,
        "title": "Completed Task",
        "status": "done",
        "priority": 2,
        "project_id": 1,
        "sprint_id": 1,
        "parent_id": None,
        "assigned_to": 1,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T02:00:00",
    }

    payload = {"status": "done"}

    response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"


def test_update_task_not_found(client, mock_task_service):
    """Test updating non-existent task."""
    mock_task_service.update_task.side_effect = HTTPException(
        status_code=404, detail="Task not found"
    )

    payload = {"title": "Updated Task"}

    response = client.patch("/tasks/999", json=payload)

    assert response.status_code == 404


def test_update_task_forbidden(client, mock_task_service):
    """Test updating task without permissions."""
    mock_task_service.update_task.side_effect = HTTPException(
        status_code=403, detail="You don't have permission to update this task"
    )

    payload = {"title": "Updated Task"}

    response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 403


def test_update_task_assign_non_member(client, mock_task_service):
    """Test assigning task to non-project member."""
    mock_task_service.update_task.side_effect = HTTPException(
        status_code=400, detail="Cannot assign task to user who is not a project member"
    )

    payload = {"assigned_to": 999}

    response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 400
    assert "not a project member" in response.json()["detail"].lower()


def test_delete_task_success(client, mock_task_service):
    """Test deleting a task."""
    mock_task_service.delete_task.return_value = None

    response = client.delete("/tasks/1")

    assert response.status_code == 204
    mock_task_service.delete_task.assert_awaited_once_with(task_id=1, user_id=1)


def test_delete_task_not_found(client, mock_task_service):
    """Test deleting non-existent task."""
    mock_task_service.delete_task.side_effect = HTTPException(
        status_code=404, detail="Task not found"
    )

    response = client.delete("/tasks/999")

    assert response.status_code == 404


def test_delete_task_forbidden(client, mock_task_service):
    """Test deleting task without permissions."""
    mock_task_service.delete_task.side_effect = HTTPException(
        status_code=403, detail="You don't have permission to delete this task"
    )

    response = client.delete("/tasks/1")

    assert response.status_code == 403
