"""Native database and domain enumeration types."""

import enum


class PathogenType(enum.StrEnum):
    """Classification of sunflower disease pathogen."""

    FUNGAL = "fungal"
    BACTERIAL = "bacterial"
    VIRAL = "viral"
    ABIOTIC = "abiotic"
    OTHER = "other"


class DiagnosisOutcome(enum.StrEnum):
    """High-level diagnosis session result."""

    MATCHED = "matched"
    NO_MATCH = "no_match"


class DiagnosisAnswer(enum.StrEnum):
    """Tri-state grower response to observed symptoms."""

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class FeedbackStatus(enum.StrEnum):
    """Triage status for grower or agronomist feedback."""

    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
