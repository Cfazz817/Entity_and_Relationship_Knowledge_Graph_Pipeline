from app.models.entity import Entity
from app.database import SessionLocal
from sqlalchemy import select
import sys
from pathlib import Path

# Ensure the app module can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))


def clean_database():
    with SessionLocal() as session:
        targets = ["Giovanni Augustino “Johnny” Cirucci",
                   "THE VATICAN AGAINST EUROPE"]

        entities_to_delete = session.execute(
            select(Entity).where(Entity.primary_name.in_(targets))
        ).scalars().all()

        if not entities_to_delete:
            print("No matching entities found to delete.")
            return

        for entity in entities_to_delete:
            print(f"Deleting Entity: {entity.primary_name}")
            session.delete(entity)

        session.commit()
        print("Cleanup complete. All associated mentions and relationships were deleted via CASCADE.")


if __name__ == "__main__":
    clean_database()
