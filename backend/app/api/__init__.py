from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .files import router as files_router
from .tasks import router as tasks_router
from .annotations import router as annotations_router

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(files_router, prefix="/files", tags=["文件管理"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(annotations_router, prefix="/tasks", tags=["标注功能"]) 