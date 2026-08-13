from fastapi import FastAPI, Query, Depends


def dependency(app : FastAPI):
    # 需求实现分页参数逻辑共有: 新闻列表和用户列表
    async def common_parameters(
            # ge 表示大于等于,le 表示小于等于
            skip: int = Query(0, ge=0),
            limit: int = Query(10, le=60)
    ):
        return {"skip": f"跳过{skip}页", "limit": limit}

    # 注入依赖
    @app.get("/news/news_list")
    async def get_news_list(commons=Depends(common_parameters)):
        return commons

    @app.get("/user/user_list")
    async def get_user_list(commons=Depends(common_parameters)):
        return commons

    # 定义依赖项
