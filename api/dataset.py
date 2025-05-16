from fastapi import HTTPException, Body
from datetime import datetime
import sqlite3
import json
from pathlib import Path
from app import app, DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/datasets")
async def get_datasets():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, created_at,messages FROM ChatHistory ORDER BY created_at DESC")
        datasets = cursor.fetchall()
        return [dict(dataset) for dataset in datasets]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

from fastapi import Body

@app.post("/api/datasets")
async def add_dataset(name: str = Body(..., embed=True), messages: str = Body(..., embed=True)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 尝试解析JSON字符串
        try:
            messages_list = json.loads(messages)
            if not isinstance(messages_list, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(status_code=422, detail="Invalid messages format, must be a valid JSON array")
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO ChatHistory (name, messages, created_at) VALUES (?, ?, ?)",
            (name, json.dumps(messages_list), created_at)
        )
        conn.commit()
        return {"id": cursor.lastrowid, "name": name, "created_at": created_at}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
