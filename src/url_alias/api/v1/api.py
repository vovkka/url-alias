from fastapi import APIRouter

from url_alias.domains.aliases.routers import router as aliases_router
from url_alias.domains.statistics.routers import router as statistics_router
from url_alias.domains.users.routers import router as users_router

api_router = APIRouter()

api_router.include_router(aliases_router)
api_router.include_router(users_router)
api_router.include_router(statistics_router)
