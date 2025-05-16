from fastapi import APIRouter
from app.api.api_v1 import auth, users, documents, tasks, annotations, exports
from app.api.api_v1.endpoints import public_files

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["annotations"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(public_files.router, prefix="/public", tags=["public_files"]) 