#!/usr/bin/env python3
"""
FastAPI 文书标注系统启动脚本
"""

import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    print(f"启动 {settings.app_name} v{settings.app_version}")
    print(f"服务地址: http://{settings.host}:{settings.port}")
    print(f"API文档: http://{settings.host}:{settings.port}/docs")
    print(f"ReDoc文档: http://{settings.host}:{settings.port}/redoc")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 