from fastapi import HTTPException


def test_get_sprint_detail_success(client, mock_sprint_service):
    """Test getting sprint detail."""
    mock_sprint_service.get_sprint_detail.return_value = {
        "id": 1,
        "title": "Sprint 1",
        "description": "Sprint Description",
        "status": "active",
        "project_id": 1,
        "start_date": "2025-12-01",
        "end_date": "2025-12-14",
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    response = client.get("/api/sprints/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Sprint 1"
    assert data["status"] == "active"


def test_get_sprint_not_found(client, mock_sprint_service):
    """Test getting non-existent sprint."""
    mock_sprint_service.get_sprint_detail.side_effect = HTTPException(
        status_code=404, detail="Sprint not found"
    )

    response = client.get("/api/sprints/999")

    assert response.status_code == 404


def test_get_sprint_forbidden(client, mock_sprint_service):
    """Test getting sprint from project user is not member of."""
    mock_sprint_service.get_sprint_detail.side_effect = HTTPException(
        status_code=403, detail="You are not a member of this project"
    )

    response = client.get("/api/sprints/1")

    assert response.status_code == 403


def test_update_sprint_success(client, mock_sprint_service):
    """Test updating a sprint."""
    mock_sprint_service.update_sprint.return_value = {
        "id": 1,
        "title": "Updated Sprint",
        "description": "Updated Description",
        "status": "completed",
        "project_id": 1,
        "start_date": "2025-12-01",
        "end_date": "2025-12-14",
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    payload = {
        "title": "Updated Sprint",
        "status": "completed",
    }

    response = client.patch("/api/sprints/1", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Sprint"
    assert data["status"] == "completed"


def test_update_sprint_not_found(client, mock_sprint_service):
    """Test updating non-existent sprint."""
    mock_sprint_service.update_sprint.side_effect = HTTPException(
        status_code=404, detail="Sprint not found"
    )

    payload = {"title": "Updated Sprint"}

    response = client.patch("/api/sprints/999", json=payload)

    assert response.status_code == 404


def test_update_sprint_forbidden(client, mock_sprint_service):
    """Test updating sprint without permissions."""
    mock_sprint_service.update_sprint.side_effect = HTTPException(
        status_code=403, detail="You don't have permission to update this sprint"
    )

    payload = {"title": "Updated Sprint"}

    response = client.patch("/api/sprints/1", json=payload)

    assert response.status_code == 403


def test_delete_sprint_success(client, mock_sprint_service):
    """Test deleting a sprint."""
    mock_sprint_service.delete_sprint.return_value = None

    response = client.delete("/api/sprints/1")

    assert response.status_code == 204
    mock_sprint_service.delete_sprint.assert_awaited_once_with(sprint_id=1, user_id=1)


def test_delete_sprint_not_found(client, mock_sprint_service):
    """Test deleting non-existent sprint."""
    mock_sprint_service.delete_sprint.side_effect = HTTPException(
        status_code=404, detail="Sprint not found"
    )

    response = client.delete("/api/sprints/999")

    assert response.status_code == 404


def test_delete_sprint_forbidden(client, mock_sprint_service):
    """Test deleting sprint without permissions."""
    mock_sprint_service.delete_sprint.side_effect = HTTPException(
        status_code=403, detail="You don't have permission to delete this sprint"
    )

    response = client.delete("/api/sprints/1")

    assert response.status_code == 403


def test_list_sprint_tasks_success(client, mock_task_service):
    """Test listing tasks in a sprint."""
    # NOTE: conftest already overrode TaskService for us!
    mock_task_service.get_project_tasks.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Task in sprint",
                "status": "in_progress",
                "priority": 2,
                "project_id": 1,
                "sprint_id": 1,
                "assigned_to": 1,
                "parent_id": None,
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }

    response = client.get("/api/sprints/1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["sprint_id"] == 1


def test_list_sprint_tasks_with_filters(client, mock_task_service):
    """Test listing sprint tasks with filters."""
    mock_task_service.get_project_tasks.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "total_pages": 0,
    }

    response = client.get("/api/sprints/1/tasks?status=done&priority=1")

    assert response.status_code == 200
    mock_task_service.get_project_tasks.assert_awaited_once()


def test_list_sprint_tasks_with_search(client, mock_task_service):
    """Test searching tasks in a sprint."""
    mock_task_service.get_project_tasks.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Bug Fix Task",
                "status": "todo",
                "priority": 3,
                "project_id": 1,
                "sprint_id": 1,
                "parent_id": None,
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }

    response = client.get("/api/sprints/1/tasks?search=bug")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
