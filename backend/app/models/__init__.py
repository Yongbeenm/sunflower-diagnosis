"""SQLAlchemy ORM models. Structure only - no business logic, no queries.

Default relationships to lazy="raise" so N+1 loads fail loudly in tests;
load explicitly with selectinload() in the repository layer.
"""

from app.models.audit import AuditLog
from app.models.auth import Permission, Role, RolePermission, User
from app.models.diagnosis import (
    DiagnosisResult,
    DiagnosisSelectedSymptom,
    DiagnosisSession,
)
from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import (
    DiagnosisAnswer,
    DiagnosisOutcome,
    FeedbackStatus,
    PathogenType,
)
from app.models.feedback import Feedback
from app.models.media import Media
from app.models.mixins import TimestampMixin
from app.models.ruleset import Ruleset
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation

__all__ = [
    "AuditLog",
    "DiagnosisAnswer",
    "DiagnosisOutcome",
    "DiagnosisResult",
    "DiagnosisSelectedSymptom",
    "DiagnosisSession",
    "Disease",
    "DiseaseSymptom",
    "Feedback",
    "FeedbackStatus",
    "Media",
    "PathogenType",
    "Permission",
    "Role",
    "RolePermission",
    "Ruleset",
    "Symptom",
    "SymptomCategory",
    "TimestampMixin",
    "Translation",
    "User",
]
