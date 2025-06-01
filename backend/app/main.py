from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from .config import settings, ensure_data_directories
from .api import api_router

# 确保数据目录存在
ensure_data_directories()

# 创建FastAPI应用 - 禁用默认的docs
app = FastAPI(
    title="Document Annotation System",
    version=settings.app_version,
    description="Document Annotation System based on FastAPI",
    docs_url=None,  # 禁用默认docs
    redoc_url=None,  # 禁用默认redoc
    openapi_url="/openapi.json"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI页面，使用国内CDN"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Document Annotation System - API Documentation",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """自定义ReDoc页面"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Document Annotation System - API Documentation",
        redoc_js_url="https://unpkg.com/redoc@2.1.3/bundles/redoc.standalone.js",
    )


@app.get("/", summary="Root Path")
async def root():
    """Root path, returns system information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "status": "running"
    }


@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "System is running normally"}


# 简单的API文档页面（备用方案）
@app.get("/simple-docs", include_in_schema=False)
async def simple_docs():
    """简单的API文档页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Annotation System - API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .method { font-weight: bold; color: #fff; padding: 5px 10px; border-radius: 3px; }
            .get { background-color: #61affe; }
            .post { background-color: #49cc90; }
            .put { background-color: #fca130; }
            .delete { background-color: #f93e3e; }
        </style>
    </head>
    <body>
        <h1>Document Annotation System API</h1>
        <p>API Documentation - <a href="/openapi.json">OpenAPI JSON</a></p>
        
        <div class="endpoint">
            <span class="method post">POST</span> /api/auth/login - User Login
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> /api/auth/register - User Registration
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> /api/auth/me - Get Current User
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> /api/users - Get Users List
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> /api/files/upload - Upload File
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> /api/tasks - Get Tasks List
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> /api/tasks - Create Task
        </div>
        
        <h3>Test the API:</h3>
        <p>You can test the API using tools like:</p>
        <ul>
            <li>curl</li>
            <li>Postman</li>
            <li>Python requests</li>
        </ul>
        
        <h3>Example:</h3>
        <pre>
# Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123","role":"admin"}'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
        </pre>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 