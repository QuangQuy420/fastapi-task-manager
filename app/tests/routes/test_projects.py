from fastapi import HTTPException


def test_create_project_success(client, mock_project_service):
    """Test successful project creation."""
    mock_project_service.create_project.return_value = {
        "id": 1,
        "title": "New Project",
        "description": "Project Description",
        "status": "planned",
        "managed_by": 1,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    payload = {
        "title": "New Project",
        "description": "Project Description",
        "status": "planned",
    }

    response = client.post("/api/projects", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Project"
    assert data["description"] == "Project Description"
    assert "id" in data
    mock_project_service.create_project.assert_awaited_once()


def test_create_project_missing_title(client):
    """Test project creation with missing title."""
    payload = {
        "description": "Description without title",
    }

    response = client.post("/api/projects", json=payload)

    assert response.status_code == 422


def test_list_projects_success(client, mock_project_service):
    """Test listing user's projects."""
    mock_project_service.get_user_projects.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Project 1",
                "description": "Description 1",
                "status": "active",
                "managed_by": 1,
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            },
            {
                "id": 2,
                "title": "Project 2",
                "description": "Description 2",
                "status": "planned",
                "managed_by": 1,
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            },
        ],
        "total": 2,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }

    response = client.get("/api/projects")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_projects_with_pagination(client, mock_project_service):
    """Test listing projects with pagination."""
    mock_project_service.get_user_projects.return_value = {
        "items": [],
        "total": 25,
        "page": 2,
        "page_size": 10,
        "total_pages": 3,
    }

    response = client.get("/api/projects?page=2&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 10
    assert data["total_pages"] == 3


def test_list_projects_filter_by_status(client, mock_project_service):
    """Test filtering projects by status."""
    mock_project_service.get_user_projects.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Active Project",
                "status": "active",
                "managed_by": 1,
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }

    response = client.get("/api/projects?status=active")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "active"


def test_list_projects_with_search(client, mock_project_service):
    """Test searching projects."""
    mock_project_service.get_user_projects.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Backend API",
                "description": "API project",
                "status": "active",
                "managed_by": 1,
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }

    response = client.get("/api/projects?search=backend")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1


def test_list_projects_with_sorting(client, mock_project_service):
    """Test sorting projects."""
    # NOTE: The reset is now handled automatically by conftest!
    mock_project_service.get_user_projects.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "total_pages": 0,
    }

    response = client.get("/api/projects?sort_by=title&order=desc")

    assert response.status_code == 200
    mock_project_service.get_user_projects.assert_awaited_once()


def test_get_project_detail_success(client, mock_project_service):
    """Test getting project detail."""
    mock_project_service.get_project_detail.return_value = {
        "id": 1,
        "title": "Test Project",
        "description": "Test Description",
        "status": "active",
        "managed_by": 1,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
        "sprints": [
            {
                "id": 1,
                "title": "Sprint 1",
                "status": "active",
                "project_id": 1,
                "start_date": "2025-12-01",
                "end_date": "2025-12-14",
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            }
        ],
    }

    response = client.get("/api/projects/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Project"
    assert "sprints" in data
    assert len(data["sprints"]) == 1


def test_get_project_not_found(client, mock_project_service):
    """Test getting non-existent project."""
    mock_project_service.get_project_detail.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )

    response = client.get("/api/projects/999")

    assert response.status_code == 404


def test_get_project_forbidden(client, mock_project_service):
    """Test getting project user is not member of."""
    mock_project_service.get_project_detail.side_effect = HTTPException(
        status_code=403, detail="You are not a member of this project"
    )

    response = client.get("/api/projects/1")

    assert response.status_code == 403


def test_update_project_success(client, mock_project_service):
    """Test updating a project."""
    mock_project_service.update_project.return_value = {
        "id": 1,
        "title": "Updated Project",
        "description": "Updated Description",
        "status": "active",
        "managed_by": 1,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    payload = {
        "title": "Updated Project",
        "description": "Updated Description",
    }

    response = client.patch("/api/projects/1", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Project"
    assert data["description"] == "Updated Description"


def test_update_project_not_found(client, mock_project_service):
    """Test updating non-existent project."""
    mock_project_service.update_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )

    payload = {"title": "Updated Title"}

    response = client.patch("/api/projects/999", json=payload)

    assert response.status_code == 404


def test_update_project_forbidden(client, mock_project_service):
    """Test updating project without permissions."""
    mock_project_service.update_project.side_effect = HTTPException(
        status_code=403, detail="You don't have permission to update this project"
    )

    payload = {"title": "Updated Title"}

    response = client.patch("/api/projects/1", json=payload)

    assert response.status_code == 403


def test_delete_project_success(client, mock_project_service):
    """Test deleting a project."""
    mock_project_service.delete_project.return_value = None

    response = client.delete("/api/projects/1")

    assert response.status_code == 204
    mock_project_service.delete_project.assert_awaited_once_with(
        project_id=1, user_id=1
    )


def test_delete_project_not_found(client, mock_project_service):
    """Test deleting non-existent project."""
    mock_project_service.delete_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )

    response = client.delete("/api/projects/999")

    assert response.status_code == 404


def test_delete_project_forbidden(client, mock_project_service):
    """Test deleting project without permissions."""
    mock_project_service.delete_project.side_effect = HTTPException(
        status_code=403, detail="Only project owner can delete"
    )

    response = client.delete("/api/projects/1")

    assert response.status_code == 403


def test_list_project_sprints_success(client, mock_sprint_service):
    """Test listing sprints in a project."""
    mock_sprint_service.get_project_sprints.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Sprint 1",
                "description": "First sprint",
                "status": "active",
                "project_id": 1,
                "start_date": "2025-12-01",
                "end_date": "2025-12-14",
                "created_at": "2025-12-11T00:00:00",
                "updated_at": "2025-12-11T00:00:00",
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }

    response = client.get("/api/projects/1/sprints")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1


def test_create_sprint_in_project_success(client, mock_sprint_service):
    """Test creating a sprint in a project."""
    mock_sprint_service.create_sprint.return_value = {
        "id": 1,
        "title": "New Sprint",
        "description": "Sprint Description",
        "status": "new",
        "project_id": 1,
        "start_date": "2025-12-01",
        "end_date": "2025-12-14",
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    payload = {
        "title": "New Sprint",
        "description": "Sprint Description",
        "start_date": "2025-12-01",
        "end_date": "2025-12-14",
    }

    response = client.post("/api/projects/1/sprints", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Sprint"
    assert data["project_id"] == 1


def test_list_project_tasks_success(client, mock_task_service):
    """Test listing tasks in a project."""
    mock_task_service.get_project_tasks.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Task description",
                "status": "todo",
                "priority": 2,
                "project_id": 1,
                "sprint_id": None,
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

    response = client.get("/api/projects/1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1


def test_create_task_in_project_success(client, mock_task_service):
    """Test creating a task in a project."""
    mock_task_service.create_task.return_value = {
        "id": 1,
        "title": "New Task",
        "description": "Task Description",
        "status": "new",
        "priority": 3,
        "project_id": 1,
        "sprint_id": None,
        "assigned_to": 1,
        "parent_id": None,
        "created_at": "2025-12-11T00:00:00",
        "updated_at": "2025-12-11T00:00:00",
    }

    payload = {
        "title": "New Task",
        "description": "Task Description",
        "status": "new",
        "priority": 3,
        "sprint_id": None,
        "assigned_to": 1,
        "parent_id": None,
    }

    response = client.post("/api/projects/1/tasks", json=payload)

    data = response.json()
    assert data["title"] == "New Task"
    assert data["project_id"] == 1
