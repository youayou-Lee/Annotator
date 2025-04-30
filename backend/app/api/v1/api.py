from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, documents, tasks, filter

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(documents.router, prefix="/documents", tags=["文书"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务"])
api_router.include_router(filter.router, prefix="/filter", tags=["过滤"]) 