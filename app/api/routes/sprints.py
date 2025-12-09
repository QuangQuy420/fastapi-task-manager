from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.sprint import SprintCreate, SprintRead, SprintUpdate
from app.services.sprint_service import SprintService


router = APIRouter(prefix="/sprints", tags=["sprints"])


@router.post(
    "",
    response_model=SprintRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sprint(
    data: SprintCreate,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(), 
):
    """
    Create a new sprint.
    """
    return sprint_service.create_sprint(data=data, user_id=current_user.id)


@router.patch(
    "/{sprint_id}",
    response_model=SprintRead,
    status_code=status.HTTP_200_OK,
)
def update_sprint(
    sprint_id: int,
    data: SprintUpdate,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """
    Update an existing sprint.
    """
    return sprint_service.update_sprint(sprint_id=sprint_id, data=data, user_id=current_user.id)


@router.delete(
    "/{sprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sprint(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """
    Delete a sprint.
    """
    sprint_service.delete_sprint(sprint_id=sprint_id, user_id=current_user.id)