## FastAPI 学习
### 为什么需要创建虚拟环境
隔离项目运行环境，避免依赖冲突，保持全局环境的稳定
### 怎么运行FastAPI项目
```angular2html
run 项目
uvicorn main:app --reload # --reload 表示自动重启服务
```
### 怎么访问FastAPI交互文档
在ip地址后添加/docs地址，可以查看可交互式文档

## 路由
URL地址和处理函数之间的映射关系，决定了当用户访问某个特定网址时，服务器应该执行哪段代码来返回结果。
FastAPI的路由定义基于Python的装饰器模式
```angular2html
@app.get("/") # app 指代FastAPI实例，get为请求方法，("/")为请求路径
async ...
```

## 接口
同一段接口逻辑，根据参数不同返回不同的数据

## 参数
参数就是客户端发送请求时附带的额外的信息和指令
参数的作用是让同一个接口能根据不同的输入，返回不同的输出，实现动态交互
+ 路径参数
  + ```angular2html
    @app.get("/book/{id}")
    async def get_book(id : int):
        return ...
    ```
  + 位置：URL路径的一部分
  + 作用：指向唯一的、特定的资源
  + 方法：GET
  + 类型注解 Path，FastAPI允许为参数声明额外的信息和校验
+ 查询参数
  + 位置：URL?之后(k1=v1&k2=v2)
  + 作用：对资源集合进行过滤、排序、分页等操作
  + 方法：GET
+ 请求体参数
  + 位置：HTTP请求的请求体中
  + 作用：创建、更新资源携带大量数据，如JSON
  + 方法：POST、PUT等
  + 在HTTP协议当中包含三个部分
    + 请求行：包含方法、URL、协议版本
    + 请求头：源数据信息(Content-Type、Authorization等)
    + 请求体：实际要发送的数据内容
  + 步骤
    + 定义类型
    + 类型注解

## 响应
默认情况下，FastAPI会自动将路径操作函数返回的Python对象，转换为JSON兼容格式