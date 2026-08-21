from sqlalchemy import select

from app.database import SessionLocal
from app.models.entity import EntityType
from app.models.institution import InstitutionCategory
from app.models.location import (
    LocationRegion,
    LocationType,
)
from app.models.relationship import RelationshipType


ENTITY_TYPES = [
    ("person", "Person"),
    ("institution", "Institution"),
    ("event", "Event"),
    ("location", "Location"),
]


INSTITUTION_CATEGORIES = [
    ("religious", "Religious"),
    ("education", "Education"),
    ("religio_educational", "Religio-Educational"),
    ("corporate", "Corporate"),
    ("nonprofit", "Non-Profit"),
    ("government", "Government"),
    ("military", "Military"),
    ("political", "Political"),
    ("healthcare", "Healthcare"),
    ("organized_crime", "Organized Crime"),
]


LOCATION_TYPES = [
    ("continent", "Continent"),
    ("country", "Country"),
    ("state_province_region", "State/Province/Region"),
    ("city", "City"),
    ("town_village", "Town/Village"),
    ("house", "House"),
    ("apartment", "Apartment"),
    ("room_space", "Room/Space"),
    ("neighborhood", "Neighborhood"),
    ("building", "Building"),
    ("street", "Street"),
    ("highway", "Highway"),
    ("park", "Park"),
    ("natural_feature", "Natural Feature/Landscape"),
    ("ocean_sea", "Ocean/Sea"),
    ("river_lake", "River/Lake"),
]


LOCATION_REGIONS = [
    ("africa", "Africa"),
    ("asia", "Asia"),
    ("europe", "Europe"),
    ("north_america", "North America"),
    ("south_america", "South America"),
    ("oceania", "Oceania"),
    ("antarctica", "Antarctica"),
]


RELATIONSHIP_TYPES = [
    ("lives_in", "Lives In", False),
    ("works_for", "Works For", False),
    ("attends", "Attends", False),
    ("member_of", "Member Of", False),
    ("leader_of", "Leader Of", False),
    ("associate_of", "Associate Of", False),
    ("interacted_with", "Interacted With", True),
    ("same_place_same_time", "Same Place Same Time", True),

    ("parent_of", "Parent Of", False),
    ("child_of", "Child Of", False),
    ("sibling_of", "Sibling Of", True),
    ("aunt_uncle_of", "Aunt/Uncle Of", False),
    ("niece_nephew_of", "Niece/Nephew Of", False),
    ("grandparent_of", "Grandparent Of", False),
    ("grandchild_of", "Grandchild Of", False),
    ("cousin_of", "Cousin Of", True),
    ("spouse_of", "Spouse Of", True),

    ("colleague_of", "Colleague Of", True),
    ("friend_of", "Friend Of", True),
    ("enemy_of", "Enemy Of", True),

    ("mentor_of", "Mentor Of", False),
    ("student_of", "Student Of", False),

    ("founder_of", "Founder Of", False),
    ("employee_of", "Employee Of", False),
    ("employer_of", "Employer Of", False),

    ("owner_of", "Owner Of", False),
    ("subordinate_of", "Subordinate Of", False),
    ("superior_of", "Superior Of", False),

    ("ally_of", "Ally Of", True),
    ("rival_of", "Rival Of", True),
    ("partner_of", "Partner Of", True),
    ("competitor_of", "Competitor Of", True),

    ("supporter_of", "Supporter Of", False),
    ("opponent_of", "Opponent Of", False),
    ("advocate_of", "Advocate Of", False),
    ("critic_of", "Critic Of", False),

    ("collaborator_of", "Collaborator Of", True),
    ("adversary_of", "Adversary Of", True),

    ("graduate_of", "Graduate Of", False),
    ("teacher_of", "Teacher Of", False),
    ("attended", "Attended", False),
]


def seed_database() -> None:

    with SessionLocal() as session:

        for code, display_name in ENTITY_TYPES:

            exists = session.scalar(
                select(EntityType).where(
                    EntityType.code == code
                )
            )

            if exists is None:

                session.add(
                    EntityType(
                        code=code,
                        display_name=display_name,
                    )
                )

        for code, display_name in INSTITUTION_CATEGORIES:

            exists = session.scalar(
                select(InstitutionCategory).where(
                    InstitutionCategory.code == code
                )
            )

            if exists is None:

                session.add(
                    InstitutionCategory(
                        code=code,
                        display_name=display_name,
                    )
                )

        for code, display_name in LOCATION_TYPES:

            exists = session.scalar(
                select(LocationType).where(
                    LocationType.code == code
                )
            )

            if exists is None:

                session.add(
                    LocationType(
                        code=code,
                        display_name=display_name,
                    )
                )

        for code, display_name in LOCATION_REGIONS:

            exists = session.scalar(
                select(LocationRegion).where(
                    LocationRegion.code == code
                )
            )

            if exists is None:

                session.add(
                    LocationRegion(
                        code=code,
                        display_name=display_name,
                    )
                )

        relationship_objects = {}

        for code, display_name, symmetric in RELATIONSHIP_TYPES:

            relationship_type = session.scalar(
                select(RelationshipType).where(
                    RelationshipType.code == code
                )
            )

            if relationship_type is None:

                relationship_type = RelationshipType(
                    code=code,
                    display_name=display_name,
                    symmetric=symmetric,
                )

                session.add(relationship_type)

            relationship_objects[code] = relationship_type

        session.flush()

        inverse_pairs = {
            "employee_of": "employer_of",
            "employer_of": "employee_of",

            "parent_of": "child_of",
            "child_of": "parent_of",

            "mentor_of": "student_of",
            "student_of": "mentor_of",

            "founder_of": "founded_by",
        }

        for code, inverse_code in inverse_pairs.items():

            current = relationship_objects.get(code)
            inverse = relationship_objects.get(inverse_code)

            if current is not None and inverse is not None:
                current.inverse_type_id = inverse.id

        session.commit()


if __name__ == "__main__":
    seed_database()
