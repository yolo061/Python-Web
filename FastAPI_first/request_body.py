from pydantic import BaseModel,Field
from fastapi import FastAPI

# 定义类型
class User(BaseModel):
    username: str = Field(default="张三",description="用户名",min_length=2,max_length=10)
    password: str = Field(min_length=3,max_length=20)

class Book(BaseModel):
    book_name : str = Field(...,min_length=2,max_length=20)
    author : str = Field(min_length=2,max_length=10)
    poster : str = Field(default="黑马出版社")
    price : int = Field(...,gt=0)

def register_request_body(app : FastAPI):
    # 完成用户的注册功能
    @app.post("/register")
    async def register(user : User):
        return user

    # 需求：设计接口新增图书，图书信息包含：书名、作者、出版社、售价
    '''
    书名 ：不能为空，长度2-20
    作者 ：长度2-10
    出版社 ： 默认值“黑马出版社”
    售价 ： 不能为空，价格大于0元
    '''
    @app.post("/addbook")
    async def addbook(book : Book):
        return book

    # 类型注解: pydantic中的Field