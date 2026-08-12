from fastapi import FastAPI, Query

def register_query_params(app : FastAPI):
    # 查询参数
    # 需求：查询新闻->分页，skip跳过的记录数，limit返回的记录数
    @app.get("/news/news_list")
    async def get_news_list(
            # 原生注解和Query注解
            # 类似于Path写法,默认值可以有具体的数
            skip : int = Query(0,description="跳过的记录数",lt=100),
            # 限制跳过记录的数量
            limit : int = Query(10,description="返回的记录数")
    ):
        return {"skip" : skip, "limit" : limit}

    # 需求：设计接口查询图书，要求携带两个查询参数：图书分类和价格
    # 参数具体要求
    # 图书分类：默认值为Python开发，长度限制5-255
    # 价格：限制大小范围50-100
    @app.get("/books/book_list")
    async def get_books_list(
            book_type : str = Query("Python开发",description="图书分类",max_length=255,min_length=5),
            price : int = Query(...,gt=49,lt=101)
    ):
        return {"types":f"图书类型为{book_type}","price":f"图书价格为{price}"}
