from fastapi import Path

def register_path_params(app):
    # 类型注解 Path
    @app.get("/book/{id}")
    async def get_book(id : int = Path(..., gt=0, lt=101, description="书籍ID，取值范围1-100")): # Path当中的参数为路径参数的校验
        # ...表示路径参数不能为空，为必填项，但是不存在默认值
        return {"id": id, "title": f"这是第{id}本书"}

    # 练习：以用户id为路径参数设计URL，要求响应结果包含用户id和名称(普通用户id)
    @app.get("/usr/{id}")
    async def get_usr(id : int):
        return {"msg" : f"普通用户{id}"}

    # 需求：查找书籍的作者，路径参数 name，长度范围2-10
    @app.get("/author/{name}")
    async def get_name(name : str=Path(...,min_length=2,max_length=10,description="作者名称，长度范围2-10")):
        return {"msg" : f"这是{name}的信息"}

    # 需求：定义两个接口，携带路径参数，并使用Path来实现类型注解
    # 接口1：以新闻分类id为参数设计URL，id范围为1-100
    # 接口2：以新闻分类名称为参数设计URL，分类名称长度为2-10
    @app.get("/news/id/{id}")
    async def get_news_id(id : int = Path(...,gt=0,lt=101,description="新闻分类id，取值范围1-100")):
        return {"msg":f"新闻id为{id}"}

    @app.get("/news/name/{name}")
    async def get_news_name(name : str = Path(...,min_length=2,max_length=10,description="新闻分类名称，长度范围2-10")):
        return {"msg":f"新闻名称为{name}"}