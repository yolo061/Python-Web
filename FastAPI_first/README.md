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
同一段接口逻辑