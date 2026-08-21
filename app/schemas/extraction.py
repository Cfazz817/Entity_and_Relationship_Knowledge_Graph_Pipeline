from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class EntityTypeEnum(str, Enum):
    PERSON = "person"
    INSTITUTION = "institution"
    EVENT = "event"
    LOCATION = "location"


class RelationshipTypeEnum(str, Enum):
    LIVES_IN = "lives_in"
    WORKS_FOR = "works_for"
    MEMBER_OF = "member_of"
    LEADER_OF = "leader_of"
    ASSOCIATE_OF = "associate_of"
    INTERACTED_WITH = "interacted_with"
    SAME_PLACE_SAME_TIME = "same_place_same_time"

    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    SIBLING_OF = "sibling_of"
    AUNT_UNCLE_OF = "aunt_uncle_of"
    NIECE_NEPHEW_OF = "niece_nephew_of"
    GRANDPARENT_OF = "grandparent_of"
    GRANDCHILD_OF = "grandchild_of"
    COUSIN_OF = "cousin_of"
    SPOUSE_OF = "spouse_of"

    COLLEAGUE_OF = "colleague_of"
    FRIEND_OF = "friend_of"
    ENEMY_OF = "enemy_of"

    MENTOR_OF = "mentor_of"
    STUDENT_OF = "student_of"

    FOUNDER_OF = "founder_of"
    EMPLOYEE_OF = "employee_of"
    EMPLOYER_OF = "employer_of"

    OWNER_OF = "owner_of"
    SUBORDINATE_OF = "subordinate_of"
    SUPERIOR_OF = "superior_of"

    ALLY_OF = "ally_of"
    RIVAL_OF = "rival_of"
    PARTNER_OF = "partner_of"

    COMPETITOR_OF = "competitor_of"
    SUPPORTER_OF = "supporter_of"
    OPPONENT_OF = "opponent_of"

    ADVOCATE_OF = "advocate_of"
    CRITIC_OF = "critic_of"

    COLLABORATOR_OF = "collaborator_of"
    ADVERSARY_OF = "adversary_of"

    GRADUATE_OF = "graduate_of"
    TEACHER_OF = "teacher_of"
    ATTENDED = "attended"


class TemporalPrecisionEnum(str, Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    DECADE = "decade"
    CIRCA = "circa"
    RANGE = "range"
    BEFORE = "before"
    AFTER = "after"
    UNKNOWN = "unknown"


class CalendarSystemEnum(str, Enum):
    GREGORIAN = "gregorian"
    JULIAN = "julian"
    HEBREW = "hebrew"
    ISLAMIC = "islamic"
    UNKNOWN = "unknown"


class EvidenceSpan(BaseModel):
    quote: str

    start_char: int | None = None

    end_char: int | None = None


class ExtractedTemporalValue(BaseModel):
    precision: TemporalPrecisionEnum

    calendar: CalendarSystemEnum = (
        CalendarSystemEnum.GREGORIAN
    )

    date_value: date | None = None

    start_date: date | None = None

    end_date: date | None = None

    year_value: int | None = None

    circa: bool = False

    original_text: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class ExtractedEntity(BaseModel):
    temporary_id: str

    entity_type: EntityTypeEnum

    name: str

    aliases: list[str] = Field(
        default_factory=list,
    )

    description: str | None = None

    birth: ExtractedTemporalValue | None = None

    death: ExtractedTemporalValue | None = None

    founding: ExtractedTemporalValue | None = None

    dissolution: ExtractedTemporalValue | None = None

    evidence: list[EvidenceSpan] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class ExtractedRelationship(BaseModel):
    temporary_id: str

    source_entity_id: str

    target_entity_id: str

    relationship_type: RelationshipTypeEnum

    validity: ExtractedTemporalValue | None = None

    evidence: list[EvidenceSpan] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity] = Field(
        default_factory=list,
    )

    relationships: list[ExtractedRelationship] = Field(
        default_factory=list,
    )
