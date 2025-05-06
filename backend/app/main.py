from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router

app = FastAPI(
    title="文书标注系统",
    description="一个用于文书数据标注、处理和训练的系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 允许前端访问响应头
)

# 注册路由
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "欢迎使用文书标注系统"}