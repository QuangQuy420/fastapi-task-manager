from typing import List

from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
)
from app.services.project_service import ProjectService
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Create a new project.

    - `managed_by` / owner is taken from the current authenticated user.
    - Also auto-adds the owner as a `ProjectMember` with role = "owner".
    """
    project = project_service.create_project(data, owner_id=current_user.id)
    return project


# @router.get(
#     "",
#     response_model=List[ProjectRead],
# )
# def list_my_projects(
#     current_user: User = Depends(get_current_user),
#     project_service: ProjectService = Depends(get_project_service),
# ):
#     """
#     List projects that the current user is a member of.
#     """
#     # You can either expose a method in ProjectService or
#     # access the repository directly like this:
#     projects = project_service.project_repo.list_for_user(current_user.id)
#     return projects


# @router.get(
#     "/{project_id}",
#     response_model=ProjectRead,
# )
# def get_project(
#     project_id: int,
#     current_user: User = Depends(get_current_user),
#     project_service: ProjectService = Depends(get_project_service),
# ):
#     """
#     Get a single project by ID (user must be a member).
#     """
#     # Service already does existence check.
#     project = project_service.get_project(project_id)

#     # Optional: enforce membership here (or move into service)
#     member = project_service.member_repo.get(project_id, current_user.id)
#     if not member:
#         from fastapi import HTTPException

#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this project",
#         )

#     return project


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Update a project.

    Only `owner` / `maintainer` (as defined in ProjectMember.role)
    are allowed – enforced inside ProjectService.
    """
    project = project_service.update_project(
        project_id=project_id,
        data=data,
        user_id=current_user.id,
    )
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Delete a project.

    Only `owner` can delete – enforced inside ProjectService.
    """
    project_service.delete_project(
        project_id=project_id,
        user_id=current_user.id,
    )
    # 204 → no body
    return None
