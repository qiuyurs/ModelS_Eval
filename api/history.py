from venv import create
from fastapi import Depends, Query
from typing import Optional
import sqlite3
from pydantic import BaseModel
from app import app

# 确保路由使用统一的app装饰器

class HistoryResponse(BaseModel):
    id: int
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    first_token_time: float
    total_time: float
    messages: list

@app.get("/api/history")
async def get_history(
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    """
    获取大模型请求记录
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页记录数
    
    返回:
    - 包含请求记录的列表
    """
    offset = (page - 1) * page_size
    
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    # 联查Models和ModelTestResults表
    query = """
    SELECT 
        mtr.id,
        m.model_name,
        mtr.prompt_tokens,
        mtr.completion_tokens,
        mtr.first_token_time,
        mtr.total_time,
        CAST(mtr.messages AS TEXT) as messages,
        CAST(mtr.response AS TEXT) as response,
        mtr.created_at
    FROM ModelTestResults mtr
    JOIN Models m ON mtr.model_id = m.id
    ORDER BY mtr.created_at DESC
    LIMIT ? OFFSET ?
    """
    
    cursor.execute(query, (page_size, offset))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        id, model_name, prompt_tokens, completion_tokens, first_token_time, total_time, messages, response,created_at = row
        
        # 直接使用数据库中的messages字段
        try:
            messages = eval(messages) if messages else []
            if not isinstance(messages, list):
                messages = []
        except:
            messages = []
        
        # 添加AI响应
        if response:
            messages.append({"role": "assistant", "content": response})
        
        result.append({
            "id": id,
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "first_token_time": first_token_time,
            "total_time": total_time,
            "messages": messages,
            "created_at": created_at
        })
    
    conn.close()
    return result