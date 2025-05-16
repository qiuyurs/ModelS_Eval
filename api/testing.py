from fastapi import HTTPException
from app import DATABASE_PATH, app
import asyncio
import time
import uuid
import json
import sqlite3
from fastapi.responses import StreamingResponse

MAKER_HANDLERS = {
    1: "openai_handler",
    2: "openai_handler",
    3: "openai_handler",
    4: "openai_handler",
    5: "openai_handler",
    6: "openai_handler",
    7: "openai_handler",
    # 8和9预留
}

async def openai_handler(model_info, chat_history, temperature, top_p, max_tokens, stream):
    from openai import AsyncOpenAI
    import tiktoken
    
    # 初始化start_time
    start_time = time.time()
    
    try:
        encoding = tiktoken.encoding_for_model(model_info["model"])
    except:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    # 预先计算prompt tokens
    prompt_tokens = sum(len(encoding.encode(msg["content"])) for msg in chat_history)
    completion_tokens = 0  # 初始化completion tokens
    
    client = AsyncOpenAI(
        api_key=model_info['api_key'],
        base_url=model_info['base_url']
    )
    
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in chat_history]
    
    if stream:
        async def generate():
            nonlocal completion_tokens
            first_token = True
            first_token_time = None
            content = ""
            
            try:
                response = await client.chat.completions.create(
                    model=model_info["model"],
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                async for chunk in response:
                    if first_token:
                        first_token_time = time.time() - start_time
                        first_token = False
                    
                    if chunk.choices and chunk.choices[0].delta.content:
                        chunk_content = chunk.choices[0].delta.content
                        content += chunk_content
                        completion_tokens += len(encoding.encode(chunk_content))
                        yield f'data: {json.dumps({"model_id": model_info["id"], "response": chunk_content})}\n\n'
                
                # 确保最终发送正确的token统计
                yield f'data: {json.dumps({"model_id": model_info["id"], "first_token_time": round(first_token_time, 2), "total_time": round(time.time() - start_time, 2), "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens})}\n\n'
                yield 'event: done\ndata: {}\n\n'
                
            except Exception as e:
                print(f"请求错误: {str(e)}")
                yield f'event: error\ndata: {json.dumps({"error": str(e), "model_id": model_info["id"]})}\n\n'
            
            finally:
                record_id = await record_test_result(
                    model_info["id"],
                    str(e) if 'e' in locals() else content,
                    prompt_tokens,
                    completion_tokens,
                    first_token_time if 'first_token_time' in locals() else 0,
                    time.time() - start_time,
                    str(uuid.uuid4()),
                    chat_history
                )
        
        return StreamingResponse(generate())
    else:
        response = await client.chat.completions.create(
            model=model_info["model"],
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=False
        )
        
        # 处理非流式响应
        content = response.choices[0].message.content
        # 更新非流式响应的Token统计
        if hasattr(response, "usage"):
            prompt_tokens = getattr(response.usage, 'prompt_tokens', prompt_tokens)
            completion_tokens = getattr(response.usage, 'completion_tokens', len(encoding.encode(content)))
        else:
            completion_tokens = len(encoding.encode(content))
        
        record_id = await record_test_result(
                    model_info["id"],
                    content,
                    prompt_tokens,
                    completion_tokens,
                    time.time() - start_time,  # first_token_time
                    time.time() - start_time,
                    str(uuid.uuid4()),
                    chat_history
                )
        
        return {
            "choices": [{"message": {"content": content}}],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }
        }

async def record_test_result(model_id, response, prompt_tokens, completion_tokens, first_token_time, total_time, request_id, messages=None):
    """记录测试结果到数据库"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ModelTestResults (
                model_id, response, prompt_tokens, completion_tokens,
                first_token_time, total_time, request_id, messages
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_id,
            response,
            prompt_tokens,
            completion_tokens,
            round(first_token_time, 2),
            round(total_time, 2),
            request_id,
            json.dumps(messages) if messages else None
        ))
        record_id = cursor.lastrowid
        conn.commit()
        return record_id
    except Exception as e:
        print(f"记录测试结果时出错: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

@app.post("/api/models/test")
async def test_model(model_test_data: dict):
    """处理多模型测试请求"""
    # 验证必填字段
    required_fields = ['model_ids', 'chatHistory']
    for field in required_fields:
        if field not in model_test_data:
            raise HTTPException(status_code=400, detail=f"缺少必填字段: {field}")
    
    # 获取模型信息
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, model, model_name, base_url, api_key, makers_id
        FROM Models
        WHERE id IN ({})
    '''.format(','.join('?' for _ in model_test_data['model_ids'])),
    model_test_data['model_ids'])
    
    models = cursor.fetchall()
    if len(models) != len(model_test_data['model_ids']):
        raise HTTPException(status_code=404, detail="部分模型未找到")
    conn.close()
    
    # 并行处理每个模型请求
    tasks = [process_model(model, model_test_data) for model in models]
    results = await asyncio.gather(*tasks)
    
    # 检查是否有流式响应
    has_streaming = any(isinstance(result, StreamingResponse) for result in results)
    
    if has_streaming:
        # 如果有流式响应，返回统一的流式响应
        async def generate():
            for result in results:
                if isinstance(result, StreamingResponse):
                    async for chunk in result.body_iterator:
                        yield chunk
                else:
                    yield f'data: {json.dumps(result)}\n\n'
            yield 'event: done\ndata: {}\n\n'
        
        return StreamingResponse(generate())
    else:
        # 否则返回普通JSON响应
        return results

async def process_model(model, model_test_data):
    """处理单个模型请求"""
    model_info = {
        "id": model[0],
        "model": model[1],
        "model_name": model[2],
        "base_url": model[3],
        "api_key": model[4],
        "makers_id": model[5]
    }
    
    handler = MAKER_HANDLERS.get(model_info["makers_id"])
    if not handler:
        raise HTTPException(status_code=400, detail=f"不支持的厂商ID: {model_info['makers_id']}")
    
    try:
        result = await globals()[handler](
            model_info,
            model_test_data['chatHistory'],
            model_test_data.get('temperature', 1),
            model_test_data.get('top_p', 0.7),
            model_test_data.get('max_tokens', 4096),
            model_test_data.get('stream', True)
        )
        
        if isinstance(result, StreamingResponse):
            return result
        else:
            return {
                "model_id": model_info["id"],
                "response": result["choices"][0]["message"]["content"],
                "prompt_tokens": result.get("usage", {}).get("prompt_tokens", len(str(model_test_data['chatHistory']))),
                "completion_tokens": result.get("usage", {}).get("completion_tokens", len(result["choices"][0]["message"]["content"])),
                "first_token_time": round(result.get("first_token_time", 0), 2),
                "total_time": round(result.get("total_time", 0), 2),
                "request_id": result.get("request_id", str(uuid.uuid4())),
                "record_id": result.get("record_id", None)
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error details - API: {model_info.get('api_key','')[:3]}***, URL: {model_info.get('base_url','')}, Model: {model_info.get('model','')}")
        print(f"Full error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_response(results):
    for result in results:
        yield f"data: {json.dumps(result)}\n\n"
        await asyncio.sleep(0.1)
    yield "data: [DONE]\n\n"
