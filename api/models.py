from fastapi import HTTPException
import sqlite3
from pathlib import Path
from app import DATABASE_PATH, app
from api.database import initialize_database

@app.on_event("startup")
async def startup_event():
    initialize_database()

@app.get("/api/models") 
async def get_models():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id, model, model_name, base_url, 
                makers, makers_id, supports_image, 
                supports_video, supports_audio, is_active, created_at
            FROM Models
            WHERE is_active = 1
        ''')
        
        models = []
        for row in cursor.fetchall():
            models.append({
                "id": row[0],
                "model": row[1],
                "model_name": row[2],
                "base_url": row[3],
                "makers": row[4],
                "makers_id": row[5],
                "supports_image": bool(row[6]),
                "supports_video": bool(row[7]),
                "supports_audio": bool(row[8]),
                "is_active": bool(row[9]),
                "created_at": row[10]
            })
        
        return {"status": "success", "data": models}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()

@app.delete("/api/models/{id}")
async def delete_model(id: int):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM Models
            WHERE id = ?
        ''', (id,))
        
        conn.commit()
        return {"status": "success", "message": "模型删除成功"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()

@app.post("/api/models")
async def add_model(model_data: dict):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 验证必填字段
        required_fields = ['model', 'model_name', 'api_key', 'base_url', 'makers', 'makers_id']
        for field in required_fields:
            if field not in model_data or not model_data[field]:
                return {"status": "error", "message": f"缺少必填字段: {field}"}
        
        # 设置默认值
        supports_image = model_data.get('supports_image', False)
        supports_video = model_data.get('supports_video', False)
        supports_audio = model_data.get('supports_audio', False)
        is_active = model_data.get('is_active', True)
        
        cursor.execute('''
            INSERT INTO Models (
                model, model_name, api_key, base_url, 
                makers, makers_id, supports_image, 
                supports_video, supports_audio, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_data['model'],
            model_data['model_name'],
            model_data['api_key'],
            model_data['base_url'],
            model_data['makers'],
            model_data['makers_id'],
            supports_image,
            supports_video,
            supports_audio,
            is_active
        ))
        
        conn.commit()
        return {"status": "success", "message": "模型添加成功"}
    except sqlite3.IntegrityError as e:
        return {"status": "error", "message": "模型已存在或数据不完整"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()
