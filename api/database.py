import sqlite3
from pathlib import Path
from app import DATABASE_PATH

def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 表结构定义
    table_definitions = {
        'Models': '''CREATE TABLE IF NOT EXISTS Models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            model_name TEXT NOT NULL,
            api_key TEXT NOT NULL,
            base_url TEXT NOT NULL,
            makers TEXT NOT NULL,
            makers_id INTEGER NOT NULL,
            supports_image BOOLEAN DEFAULT 0,
            supports_video BOOLEAN DEFAULT 0,
            supports_audio BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''',
        'ModelTestResults': '''CREATE TABLE IF NOT EXISTS ModelTestResults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            messages TEXT NOT NULL,
            response TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            first_token_time REAL NOT NULL,
            total_time REAL NOT NULL,
            request_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''',
        'ChatHistory': '''CREATE TABLE IF NOT EXISTS ChatHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            messages TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )'''
    }
    
    # 检查并创建表
    for table_name, table_def in table_definitions.items():
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            cursor.execute(table_def)
        else:
            # 检查字段是否存在，不存在则添加
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # 解析表定义获取字段列表
            import re
            columns = re.findall(r'(\w+)\s+[^,\n]+(?:,|\n|$)', table_def.split('(')[1].split(')')[0])
            
            for column in columns:
                if column not in existing_columns:
                    # 获取字段类型
                    column_type = re.search(fr'{column}\s+([^,\n]+)', table_def).group(1)
                    # 检查是否为NOT NULL字段
                    if 'NOT NULL' in column_type:
                        # 对于NOT NULL字段，添加DEFAULT值
                        if 'TEXT' in column_type:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type.replace('NOT NULL', '')} DEFAULT ''")
                        elif 'INTEGER' in column_type or 'BOOLEAN' in column_type:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type.replace('NOT NULL', '')} DEFAULT 0")
                        else:
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type.replace('NOT NULL', '')}")
                    else:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type}")
    
    conn.commit()
    conn.close()
