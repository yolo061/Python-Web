from fastapi import FastAPI, HTTPException

def register_error(app : FastAPI):
    @app.get("/news/{id}")
    # 需求：按照id查询新闻(1-6)
    async def get_news(id : int):
        id_list = [1,2,3,4,5,6]
        if id not in id_list:
            raise HTTPException(status_code=404, detail="当前id不存在")
        return {"id" : id}