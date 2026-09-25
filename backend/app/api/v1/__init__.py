"""Version 1 of the public API. Breaking changes go in a v2 package."""

from fastapi import APIRouter

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.ai import router as ai_router
from app.api.v1.routes.analytics import router as analytics_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.diagnosis import router as diagnosis_router
from app.api.v1.routes.diseases import router as diseases_router
from app.api.v1.routes.feedback import router as feedback_router
from app.api.v1.routes.media import router as media_router
from app.api.v1.routes.public import router as public_router
from app.api.v1.routes.symptoms import router as symptoms_router
from app.api.v1.routes.users import router as users_router

router = APIRouter()

router.include_router(public_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(diagnosis_router)
router.include_router(diseases_router)
router.include_router(symptoms_router)
router.include_router(media_router)
router.include_router(analytics_router)
router.include_router(feedback_router)
router.include_router(ai_router)
router.include_router(admin_router)
