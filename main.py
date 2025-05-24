from fastapi import FastAPI,Request
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
from settings import orm
from contextlib import asynccontextmanager
from utils.redis import connection_redis, close_redis
import time
from apps.user import user
from apps.agents import agents
from apps.ai import ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connection_redis()
    yield
    await close_redis()
app=FastAPI(title='智能体后端API',summary='这是关于构造智能体的后端接口',version='0.1.1',lifespan=lifespan,docs_url='/')

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    return response

register_tortoise(app=app,config=orm)

# agent_app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(router=user,prefix='/user',tags=['用户模块'])
app.include_router(router=agents,prefix='/agents',tags=['智能体模块'])
app.include_router(router=ai,prefix='/agents',tags=['智能体模块'])


# if __name__ == '__main__':
#     uvicorn.run(app='main:app',host='127.0.0.1',port=8000,reload=True)