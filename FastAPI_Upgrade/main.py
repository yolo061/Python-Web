from fastapi import FastAPI
from dependency import dependency
from orm_01 import register_orm
from orm_06_router import register_book_router

app = FastAPI()

@app.middleware("http")
async def middleware1(request, call_next):
    print("中间件1 start")
    response = await call_next(request) # await 表示异步步骤
    print("中间件1 end")
    return response

@app.middleware("http")
async def middleware2(request, call_next):
    print("中间件2 start")
    response = await call_next(request) # await 表示异步步骤
    print("中间件2 end")
    return response

# 中间件是按照代码顺序自底向上执行

# 依赖项代码
dependency(app)

# orm创建数据库
register_orm(app)

# 注册书籍管理路由
register_book_router(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
