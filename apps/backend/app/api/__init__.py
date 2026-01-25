from fastapi import APIRouter

from app.api.routes import api_keys, auth, dashboard, health, notam, tasks, training

router = APIRouter()
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(notam.router)
router.include_router(dashboard.router)
router.include_router(tasks.router)
router.include_router(api_keys.router)
router.include_router(training.router)
