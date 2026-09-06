from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.entity import Entity, EntityType

def check_event_entities():
    with SessionLocal() as session:
        # Query to count entities grouped by their type
        results = session.execute(
            select(
                EntityType.display_name,
                func.count(Entity.id).label('entity_count')
            )
            .join(Entity, isouter=True) # outer join to see types with 0 entities
            .group_by(EntityType.display_name)
            .order_by(func.count(Entity.id).desc())
        ).all()

        print("\n--- Entity Counts by Type ---")
        event_count = 0
        for type_name, count in results:
            print(f"{type_name}: {count}")
            if type_name.lower() == 'event':
                event_count = count
        
        print("\n--- Conclusion ---")
        if event_count > 0:
            print(f"Yes, events are registering. There are currently {event_count} events in the database.")
        else:
            print("No, there are currently 0 event entities registered in the database.")

if __name__ == "__main__":
    check_event_entities()
