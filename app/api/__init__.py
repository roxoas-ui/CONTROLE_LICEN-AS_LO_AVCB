from fastapi import APIRouter

from app.api import auth, avcb, dashboard, licenses, reports, residues, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(licenses.router)
api_router.include_router(avcb.router)
api_router.include_router(residues.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
