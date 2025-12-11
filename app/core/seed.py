import argparse
import random
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import insert, text

from app.core.db import SessionLocal
from app.core.enums import (
    HistoryAction,
    ProjectStatus,
    SprintStatus,
    TaskPriority,
    TaskStatus,
    UserRole,
)
from app.models.project import Project
from app.models.project_history import ProjectHistory
from app.models.project_member import ProjectMember
from app.models.sprint import Sprint
from app.models.sprint_history import SprintHistory
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.models.user import User

try:
    from faker import Faker

    _FAKER = Faker()
except Exception:
    _FAKER = None


def _make_user(i: int) -> dict:
    """Generate fake user data."""
    email = _FAKER.email() if _FAKER else f"user{i}@example.com"
    full_name = _FAKER.name() if _FAKER else f"User {i}"

    return {
        "email": email,
        "full_name": full_name,
        "hashed_password": "$2b$12$DUpbLLF5Jcco6agJ73c.G.eJs08iEvD/WEyAKCNOBaBBaYAHa1t7y",  # dummy bcrypt hash
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


def _make_project(i: int, user_ids: list[int]) -> dict:
    """Generate fake project data."""
    title = _FAKER.catch_phrase() if _FAKER else f"Project {i}"
    description = (
        _FAKER.paragraph(nb_sentences=3) if _FAKER else f"Description for project {i}"
    )
    status = random.choice(list(ProjectStatus)).value
    managed_by = random.choice(user_ids)

    return {
        "title": title,
        "description": description,
        "status": status,
        "managed_by": managed_by,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": random.choice(
            [None, datetime.now() - timedelta(days=random.randint(1, 100))]
        ),
    }


def _make_project_member(
    project_id: int, user_ids: list[int], existing_members: set
) -> Optional[dict]:
    """Generate fake project member data."""
    available_users = [
        uid for uid in user_ids if (project_id, uid) not in existing_members
    ]
    if not available_users:
        return None

    user_id = random.choice(available_users)
    role = random.choice(list(UserRole)).value

    existing_members.add((project_id, user_id))

    return {
        "project_id": project_id,
        "user_id": user_id,
        "role": role,
    }


def _make_sprint(i: int, project_id: int) -> dict:
    """Generate fake sprint data."""
    title = _FAKER.sentence(nb_words=4) if _FAKER else f"Sprint {i}"
    description = _FAKER.paragraph(nb_sentences=2) if _FAKER else None
    status = random.choice(list(SprintStatus)).value

    start_date = date.today() + timedelta(days=random.randint(-90, 30))
    end_date = start_date + timedelta(days=random.randint(7, 21))

    return {
        "project_id": project_id,
        "title": title,
        "description": description,
        "status": status,
        "start_date": start_date,
        "end_date": end_date,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": random.choice(
            [None, datetime.now() - timedelta(days=random.randint(1, 60))]
        ),
    }


def _make_task(
    i: int, project_id: int, sprint_ids: list[int], user_ids: list[int]
) -> dict:
    """Generate fake task data."""
    title = _FAKER.sentence(nb_words=6) if _FAKER else f"Task #{i}"
    description = _FAKER.paragraph(nb_sentences=2) if _FAKER else None
    status = random.choice(list(TaskStatus)).value
    priority = random.choice(list(TaskPriority)).value

    # 70% chance of being in a sprint
    sprint_id = (
        random.choice(sprint_ids) if random.random() < 0.7 and sprint_ids else None
    )

    # 60% chance of being assigned
    assigned_to = random.choice(user_ids) if random.random() < 0.6 else None

    # 50% chance of having a due date
    due_date = None
    if random.random() < 0.5:
        due_date = datetime.now() + timedelta(days=random.randint(1, 180))

    return {
        "project_id": project_id,
        "sprint_id": sprint_id,
        "parent_id": None,  # Skip parent tasks for simplicity
        "assigned_to": assigned_to,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "due_date": due_date,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "deleted_at": None,
    }


def _make_project_history(project_id: int, user_ids: list[int]) -> dict:
    """Generate fake project history data."""
    changed_by = random.choice(user_ids)
    action = random.choice(list(HistoryAction)).value

    details = {
        "title": _FAKER.catch_phrase() if _FAKER else "Project",
        "status": random.choice(list(ProjectStatus)).value,
    }

    return {
        "project_id": project_id,
        "changed_by": changed_by,
        "changed_at": datetime.now() - timedelta(days=random.randint(0, 90)),
        "action": action,
        "details": details,
    }


def _make_sprint_history(sprint_id: int, user_ids: list[int]) -> dict:
    """Generate fake sprint history data."""
    changed_by = random.choice(user_ids)
    action = random.choice(list(HistoryAction)).value

    details = {
        "title": _FAKER.sentence(nb_words=4) if _FAKER else "Sprint",
        "status": random.choice(list(SprintStatus)).value,
    }

    return {
        "sprint_id": sprint_id,
        "changed_by": changed_by,
        "changed_at": datetime.now() - timedelta(days=random.randint(0, 60)),
        "action": action,
        "details": details,
    }


def _make_task_history(task_id: int, user_ids: list[int]) -> dict:
    """Generate fake task history data."""
    changed_by = random.choice(user_ids)
    action = random.choice(list(HistoryAction)).value

    details = {
        "status": random.choice(list(TaskStatus)).value,
        "priority": random.choice(list(TaskPriority)).value,
        "assigned_to": random.choice(user_ids) if random.random() < 0.5 else None,
    }

    return {
        "task_id": task_id,
        "changed_by": changed_by,
        "changed_at": datetime.now() - timedelta(days=random.randint(0, 30)),
        "action": action,
        "details": details,
    }


def seed_all(
    num_users: int = 1000,
    num_projects: int = 500,
    sprints_per_project: int = 50,
    tasks_per_project: int = 1000,
    members_per_project: int = 100,
    histories_per_entity: int = random.randint(3, 8),
    truncate: bool = False,
):
    """
    Seed all tables with related data.
    """
    sess = SessionLocal()

    try:
        if truncate:
            print("Truncating all tables...")
            sess.execute(text("TRUNCATE TABLE task_history RESTART IDENTITY CASCADE"))
            sess.execute(text("TRUNCATE TABLE sprint_history RESTART IDENTITY CASCADE"))
            sess.execute(
                text("TRUNCATE TABLE project_history RESTART IDENTITY CASCADE")
            )
            sess.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
            sess.execute(text("TRUNCATE TABLE sprints RESTART IDENTITY CASCADE"))
            sess.execute(
                text("TRUNCATE TABLE project_members RESTART IDENTITY CASCADE")
            )
            sess.execute(text("TRUNCATE TABLE projects RESTART IDENTITY CASCADE"))
            sess.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
            sess.commit()

        # 1. Create Users
        print(f"Creating {num_users} users...")
        user_batch = [_make_user(i) for i in range(1, num_users + 1)]
        sess.execute(insert(User), user_batch)
        sess.commit()

        # Get user IDs
        user_ids = [
            row[0] for row in sess.execute(text("SELECT id FROM users")).fetchall()
        ]
        print(f"Created {len(user_ids)} users")

        # 2. Create Projects
        print(f"Creating {num_projects} projects...")
        project_batch = [_make_project(i, user_ids) for i in range(1, num_projects + 1)]
        sess.execute(insert(Project), project_batch)
        sess.commit()

        # Get project IDs
        project_ids = [
            row[0] for row in sess.execute(text("SELECT id FROM projects")).fetchall()
        ]
        print(f"Created {len(project_ids)} projects")

        # 3. Create Project Members
        print("Creating project members...")
        existing_members = set()
        all_members = []

        for project_id in project_ids:
            for _ in range(members_per_project):
                member_data = _make_project_member(
                    project_id, user_ids, existing_members
                )
                if member_data:
                    all_members.append(member_data)

        if all_members:
            # Insert in batches
            batch_size = 1000
            for i in range(0, len(all_members), batch_size):
                batch = all_members[i : i + batch_size]
                sess.execute(insert(ProjectMember), batch)
                sess.commit()
        print(f"Created {len(all_members)} project members")

        # 4. Create Sprints
        print("Creating sprints...")
        all_sprints = []
        for project_id in project_ids:
            for i in range(sprints_per_project):
                all_sprints.append(_make_sprint(i, project_id))

        batch_size = 1000
        for i in range(0, len(all_sprints), batch_size):
            batch = all_sprints[i : i + batch_size]
            sess.execute(insert(Sprint), batch)
            sess.commit()

        # Get sprint IDs per project
        sprint_by_project = {}
        for project_id in project_ids:
            sprint_ids = [
                row[0]
                for row in sess.execute(
                    text(f"SELECT id FROM sprints WHERE project_id = {project_id}")
                ).fetchall()
            ]
            sprint_by_project[project_id] = sprint_ids
        print(f"Created {len(all_sprints)} sprints")

        # 5. Create Tasks
        print("Creating tasks...")
        all_tasks = []
        for project_id in project_ids:
            sprint_ids = sprint_by_project.get(project_id, [])
            for i in range(tasks_per_project):
                all_tasks.append(_make_task(i, project_id, sprint_ids, user_ids))

        batch_size = 5000
        for i in range(0, len(all_tasks), batch_size):
            batch = all_tasks[i : i + batch_size]
            sess.execute(insert(Task), batch)
            sess.commit()
            print(
                f"  Inserted {min(i + batch_size, len(all_tasks))}/{len(all_tasks)} tasks"
            )

        task_ids = [
            row[0] for row in sess.execute(text("SELECT id FROM tasks")).fetchall()
        ]
        print(f"Created {len(task_ids)} tasks")

        # 6. Create Project Histories
        print("Creating project histories...")
        all_project_histories = []
        for project_id in project_ids:
            for _ in range(histories_per_entity):
                all_project_histories.append(
                    _make_project_history(project_id, user_ids)
                )

        batch_size = 1000
        for i in range(0, len(all_project_histories), batch_size):
            batch = all_project_histories[i : i + batch_size]
            sess.execute(insert(ProjectHistory), batch)
            sess.commit()
        print(f"Created {len(all_project_histories)} project histories")

        # 7. Create Sprint Histories
        print("Creating sprint histories...")
        all_sprint_histories = []
        for sprint_ids in sprint_by_project.values():
            for sprint_id in sprint_ids:
                for _ in range(histories_per_entity):
                    all_sprint_histories.append(
                        _make_sprint_history(sprint_id, user_ids)
                    )

        batch_size = 1000
        for i in range(0, len(all_sprint_histories), batch_size):
            batch = all_sprint_histories[i : i + batch_size]
            sess.execute(insert(SprintHistory), batch)
            sess.commit()
        print(f"Created {len(all_sprint_histories)} sprint histories")

        # 8. Create Task Histories
        print("Creating task histories...")
        all_task_histories = []
        for task_id in task_ids[
            : min(10000, len(task_ids))
        ]:  # Limit to avoid too much data
            for _ in range(histories_per_entity):
                all_task_histories.append(_make_task_history(task_id, user_ids))

        batch_size = 5000
        for i in range(0, len(all_task_histories), batch_size):
            batch = all_task_histories[i : i + batch_size]
            sess.execute(insert(TaskHistory), batch)
            sess.commit()
            print(
                f"  Inserted {min(i + batch_size, len(all_task_histories))}/{len(all_task_histories)} task histories"
            )
        print(f"Created {len(all_task_histories)} task histories")

        print("\n✅ Seeding completed successfully!")
        print("Summary:")
        print(f"  - Users: {len(user_ids)}")
        print(f"  - Projects: {len(project_ids)}")
        print(f"  - Project Members: {len(all_members)}")
        print(f"  - Sprints: {len(all_sprints)}")
        print(f"  - Tasks: {len(task_ids)}")
        print(
            f"  - Histories: {len(all_project_histories) + len(all_sprint_histories) + len(all_task_histories)}"
        )

    except Exception as e:
        sess.rollback()
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        sess.close()


def main():
    parser = argparse.ArgumentParser(description="Seed the database with fake data.")
    parser.add_argument(
        "--users", type=int, default=900, help="Number of users to create"
    )
    parser.add_argument(
        "--projects", type=int, default=500, help="Number of projects to create"
    )
    parser.add_argument(
        "--sprints-per-project", type=int, default=50, help="Sprints per project"
    )
    parser.add_argument(
        "--tasks-per-project", type=int, default=1000, help="Tasks per project"
    )
    parser.add_argument(
        "--members-per-project", type=int, default=100, help="Members per project"
    )
    parser.add_argument(
        "--histories", type=int, default=5, help="History records per entity"
    )
    parser.add_argument(
        "--truncate", action="store_true", help="Truncate all tables before seeding"
    )

    args = parser.parse_args()

    seed_all(
        num_users=args.users,
        num_projects=args.projects,
        sprints_per_project=args.sprints_per_project,
        tasks_per_project=args.tasks_per_project,
        members_per_project=args.members_per_project,
        histories_per_entity=args.histories,
        truncate=args.truncate,
    )


if __name__ == "__main__":
    main()
