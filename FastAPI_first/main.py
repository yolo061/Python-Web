from fastapi import FastAPI
from path_params import register_path_params
from query_params import register_query_params
from request_body import register_request_body
from response_params import register_response
from error_params import register_error

# 创建 FastAPI实例
app = FastAPI()

# 注册路径参数路由
register_path_params(app)

# 注册查询参数路由
register_query_params(app)

# 注册请求体参数路由
register_request_body(app)

# 响应类型设置
# register_response(app)

# 异常响应
register_error(app)
@app.get("/")
# async 表示异步
async def root():
    return {"message": "Hello World"}

# 访问 /hello，响应结果 msg: 你好 FastAPI
@app.get("/hello")
async def get_hello():
    return {"msg" : "你好 FastAPI"}