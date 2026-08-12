from fastapi import FastAPI

# 创建 FastAPI实例
app = FastAPI()


@app.get("/")
# async 表示异步
async def root():
    return {"message": "Hello World"}

# 访问 /hello，响应结果 msg: 你好 FastAPI
@app.get("/hello")
async def get_hello():
    return {"msg" : "你好 FastAPI"}
