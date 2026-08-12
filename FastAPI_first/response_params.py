from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

class News(BaseModel):
    id : int
    title : str
    content : str


def register_response(app : FastAPI):
    @app.get("/html", response_class=HTMLResponse)
    async def get_html():
        return "<h1>Hello Python</h1>" # 只能响应HTML代码

    @app.get("/file", response_class=FileResponse)
    async def get_file():
        # 需求 ：返回一个图片内容
        file_path = "./files/ico.png"
        return FileResponse(file_path)

    # 自定义响应类型
    @app.get("/news/{id}", response_model=News)
    async def get_news(id : int):
        return {
            "id" : id,
            "title" : f"这是第{id}本书",
            "content" : "这是一本好书"
        }