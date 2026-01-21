from datetime import datetime
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.models import BackgroundTask, User
from app.db.session import engine, init_db


def main() -> None:
    init_db()
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.email == "admin@aeronlp.local")).first()
        if not admin:
            user = User(
                email="admin@aeronlp.local",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            session.add(user)
            session.commit()
        tasks = [
            BackgroundTask(task_type="notam_parse", status="pending", detail="Seeded task"),
            BackgroundTask(task_type="alert_scan", status="running", detail="Seeded task"),
        ]
        for task in tasks:
            session.add(task)
        session.commit()
    print("Seed complete")


if __name__ == "__main__":
    main()
