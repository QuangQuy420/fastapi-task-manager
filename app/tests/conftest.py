from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.services.project_service import ProjectService
from app.services.sprint_service import SprintService
from app.services.task_service import TaskService
from app.services.user_service import UserService


# --- 1. Define Fresh Mocks for Every Test ---
@pytest.fixture(scope="function")
def mock_user_service():
    return AsyncMock(spec=UserService)


@pytest.fixture(scope="function")
def mock_project_service():
    return AsyncMock(spec=ProjectService)


@pytest.fixture(scope="function")
def mock_sprint_service():
    return AsyncMock(spec=SprintService)


@pytest.fixture(scope="function")
def mock_task_service():
    return AsyncMock(spec=TaskService)


@pytest.fixture(scope="function")
def mock_current_user():
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    return user


# --- 2. Define Client with Overrides ---
@pytest.fixture(scope="function")
def client(
    mock_user_service,
    mock_project_service,
    mock_sprint_service,
    mock_task_service,
    mock_current_user,
):
    # Override dependencies
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[ProjectService] = lambda: mock_project_service
    app.dependency_overrides[SprintService] = lambda: mock_sprint_service
    app.dependency_overrides[TaskService] = lambda: mock_task_service
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    with TestClient(app) as c:
        yield c

    # Clean up after test
    app.dependency_overrides.clear()
