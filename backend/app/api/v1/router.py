from fastapi import APIRouter

from app.api.v1.scenario import router as scenario_router
from app.api.v1.ai_recommendations import router as ai_recommendations_router
from app.api.v1.ai import router as ai_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.decision import router as decision_router
from app.api.v1.financial import router as financial_router
from app.api.v1.health import router as health_router
from app.api.v1.organization import router as organization_router
from app.api.v1.recommendation import router as recommendation_router
from app.api.v1.report import router as report_router
from app.api.v1.risk import router as risk_router
from app.api.v1.simulation import router as simulation_router
from app.api.v1.timeline import router as timeline_router
from app.api.v1.user import router as user_router
from app.api.v1.waste import router as waste_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(ai_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(organization_router)
api_v1_router.include_router(decision_router)
api_v1_router.include_router(ai_recommendations_router)
api_v1_router.include_router(department_router)
api_v1_router.include_router(financial_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(waste_router)
api_v1_router.include_router(risk_router)
api_v1_router.include_router(simulation_router)
api_v1_router.include_router(scenario_router)
api_v1_router.include_router(report_router)
api_v1_router.include_router(recommendation_router)
api_v1_router.include_router(timeline_router)
api_v1_router.include_router(user_router)
