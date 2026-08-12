from fastapi import FastAPI
from path_params import register_path_params

# 创建 FastAPI实例
app = FastAPI()

# 注册路径参数路由
register_path_params(app)


@app.get("/")
# async 表示异步
async def root():
    return {"message": "Hello World"}

# 访问 /hello，响应结果 msg: 你好 FastAPI
@app.get("/hello")
async def get_hello():
    return {"msg" : "你好 FastAPI"}