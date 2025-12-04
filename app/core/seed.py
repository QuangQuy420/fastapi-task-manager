import argparse
import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import insert, text

from app.core.db import SessionLocal, engine
from app.models.task import Task
from app.core.enums import TaskStatus, TaskPriority

try:
    from faker import Faker

    _FAKER = Faker()
except Exception:
    _FAKER = None


def _make_task(i: int) -> dict:
    title = _FAKER.sentence(nb_words=6) if _FAKER else f"Task #{i}"
    description = _FAKER.paragraph(nb_sentences=2) if _FAKER else None

    # random status / priority
    status = random.choice(list(TaskStatus)).value
    priority = random.choice(list(TaskPriority)).value

    # occasionally assign to someone
    assigned_to: Optional[str]
    if _FAKER and random.random() < 0.6:
        assigned_to = _FAKER.email()
    elif not _FAKER and random.random() < 0.6:
        assigned_to = f"user{random.randint(1,1000)}@example.com"
    else:
        assigned_to = None

    # occasional due date within next 180 days
    due_date = None
    if random.random() < 0.5:
        due_date = datetime.now() + timedelta(days=random.randint(1, 180))

    is_completed = status == TaskStatus.DONE.value and random.random() < 0.9

    now = datetime.now()

    return {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "assigned_to": assigned_to,
        "due_date": due_date,
        "is_completed": is_completed,
        "created_at": now,
        "updated_at": now,
    }


def seed(count: int = 100_000, batch_size: int = 5_000, truncate: bool = False):
    """
    Insert `count` Task records in batches. Uses SQLAlchemy core bulk insert for speed.
    """
    sess = SessionLocal()

    try:
        if truncate:
            # Postgres-specific truncate to reset ids quickly
            sess.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
            sess.commit()

        inserted = 0
        while inserted < count:
            n = min(batch_size, count - inserted)
            batch = [_make_task(inserted + i + 1) for i in range(n)]
            sess.execute(insert(Task), batch)
            sess.commit()
            inserted += n
            print(f"Inserted {inserted}/{count}")
    finally:
        sess.close()


def main():
    parser = argparse.ArgumentParser(description="Seed the DB with fake tasks.")
    parser.add_argument("--count", type=int, default=100_000, help="Number of tasks to create")
    parser.add_argument("--batch-size", type=int, default=5_000, help="Insert batch size")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate tasks table before seeding (resets ids).",
    )
    args = parser.parse_args()
    seed(count=args.count, batch_size=args.batch_size, truncate=args.truncate)


if __name__ == "__main__":
    main()