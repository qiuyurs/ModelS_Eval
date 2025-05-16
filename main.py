from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app import app

# 配置静态文件路由
app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="assets")

# 确保所有API路由都被正确注册
# 假设 database 模块在 app 包下，尝试修改导入路径
from api.database import initialize_database
from api.models import get_models, delete_model, add_model
from api.testing import test_model
from api.history import get_history
from api.dataset import get_datasets

@app.get("/")
async def root():
    """
    根路由接口
    
    功能: 返回前端首页HTML文件
    
    输入参数: 无
    
    返回:
        FileResponse: 返回templates/index.html文件内容
    
    使用场景: 前端应用入口，用于加载Vue应用
    """
    return FileResponse("static/dist/index.html")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """
    通配路由接口
    
    功能: 捕获所有前端路由请求并返回index.html
    
    输入参数:
        full_path: 前端路由路径
    
    返回:
        FileResponse: 返回templates/index.html文件内容
    
    使用场景: 前端路由处理，用于Vue应用的路由跳转
    """
    return FileResponse("static/dist/index.html")
