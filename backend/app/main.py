from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# 设置CORS - 在开发环境中简化配置
origins = [
    "http://localhost:3000",    # 前端开发服务器
    "http://127.0.0.1:3000",
    "http://localhost:8000",    # 后端服务
    "http://127.0.0.1:8000",
    # 添加其他可能的源
    "http://localhost",
    "http://127.0.0.1",
    "*"  # 在开发阶段允许所有来源，生产环境应移除
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 暴露所有响应头
)

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {"message": "Welcome to Annotator API"}

# 使用此代码直接启动服务（仅开发环境使用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 