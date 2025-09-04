"""FastAPI应用主文件"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import Dict, Any

from .routes import router
from .middleware import setup_middleware
from ..core.config import get_settings
from ..core.logger import get_logger, setup_logger
from ..models.manager import get_model_manager
from ..plugins.manager import get_plugin_manager

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动DocuMind Web服务...")
    
    try:
        # 初始化配置
        settings = get_settings()
        
        # 设置日志
        setup_logger(
            level=settings.logging.level,
            log_file=settings.logging.file_path,
            rotation=settings.logging.rotation,
            retention=settings.logging.retention
        )
        
        # 初始化插件管理器
        plugin_manager = get_plugin_manager()
        await plugin_manager.load_plugins_from_config(settings.dict())
        
        # 初始化模型管理器
        model_manager = get_model_manager()
        
        logger.info("DocuMind Web服务启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    
    finally:
        logger.info("关闭DocuMind Web服务...")
        
        try:
            # 清理插件管理器
            plugin_manager = get_plugin_manager()
            await plugin_manager.shutdown()
            
            # 清理模型管理器
            model_manager = get_model_manager()
            await model_manager.unload_all_models()
            
            logger.info("DocuMind Web服务关闭完成")
        
        except Exception as e:
            logger.error(f"服务关闭失败: {e}")

def create_app() -> FastAPI:
    """创建FastAPI应用
    
    Returns:
        FastAPI应用实例
    """
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title="DocuMind API",
        description="智能文档解析系统API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # 设置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.web.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 设置中间件
    setup_middleware(app)
    
    # 注册路由
    app.include_router(router, prefix="/api/v1")
    
    # 静态文件服务
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # 前端页面
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        """主页"""
        html_file = Path(__file__).parent / "templates" / "index.html"
        if html_file.exists():
            return html_file.read_text(encoding="utf-8")
        else:
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>DocuMind - 智能文档解析系统</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; text-align: center; margin-bottom: 30px; }
                    .feature { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
                    .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    .api-link:hover { background: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 DocuMind 智能文档解析系统</h1>
                    
                    <div class="feature">
                        <h3>📄 PDF文档解析</h3>
                        <p>智能提取PDF文档的目录结构，支持带页码和不带页码的目录提取。</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🤖 多模型支持</h3>
                        <p>支持Qwen2.5-VL等多种视觉语言模型，可通过插件扩展更多模型。</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🔧 插件化架构</h3>
                        <p>模块化设计，支持自定义模型插件和处理器插件。</p>
                    </div>
                    
                    <div class="feature">
                        <h3>⚡ 批量处理</h3>
                        <p>支持批量处理多个文档，提高工作效率。</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <a href="/docs" class="api-link">📚 API文档</a>
                        <a href="/redoc" class="api-link">📖 ReDoc文档</a>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": "DocuMind API",
            "version": "1.0.0"
        }
    
    return app

def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1
):
    """运行Web服务器
    
    Args:
        host: 服务器地址
        port: 服务器端口
        reload: 是否启用热重载
        workers: 工作进程数
    """
    settings = get_settings()
    
    # 使用配置中的设置
    host = host or settings.web.host
    port = port or settings.web.port
    
    uvicorn.run(
        "agentdoc.api.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info"
    )

if __name__ == "__main__":
    run_server(reload=True)