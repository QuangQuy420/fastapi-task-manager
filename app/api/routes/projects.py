from typing import List
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.services.project_service import ProjectService
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(), 
):
    """
    Create a new project.
    - `managed_by` / owner is taken from the current authenticated user.
    - Also auto-adds the owner as a `ProjectMember` with role = "owner".
    """
    return project_service.create_project(data, owner_id=current_user.id)


@router.get(
    "", 
    response_model=List[ProjectRead], 
    status_code=status.HTTP_200_OK,
)
def list_my_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """
    List projects that the current user is a member of.
    """
    return project_service.get_user_projects(current_user.id)


@router.get(
    "/{project_id}", 
    response_model=ProjectRead, 
    status_code=status.HTTP_200_OK,
)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """
    Get a single project by ID (user must be a member).
    """
    return project_service.get_project_detail(project_id, current_user.id)


@router.patch(
    "/{project_id}", 
    response_model=ProjectRead, 
    status_code=status.HTTP_200_OK,
)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """
    Update a project.
    Only `owner` / `maintainer` are allowed.
    """
    return project_service.update_project(
        project_id=project_id,
        data=data,
        user_id=current_user.id,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """
    Delete a project.
    Only `owner` can delete.
    """
    project_service.delete_project(
        project_id=project_id,
        user_id=current_user.id,
    )
    return None