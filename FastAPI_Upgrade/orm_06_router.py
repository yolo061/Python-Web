# =============================================================================
# ORM + FastAPI 路由集成 (orm_06_router.py)
# =============================================================================
#
# 【本文件的作用】
# 将前面学到的 ORM 知识整合到 FastAPI 路由中，提供完整的 RESTful API 示例。
#
# 【RESTful API 设计规范】
# ┌──────────┬──────────────┬─────────────────────────────────┐
# │ HTTP 方法 │ 路径          │ 说明                             │
# ├──────────┼──────────────┼─────────────────────────────────┤
# │ POST     │ /books       │ 创建新书籍（Create）              │
# │ GET      │ /books       │ 获取书籍列表（Read）              │
# │ GET      │ /books/{id}  │ 获取单个书籍（Read）              │
# │ PUT      │ /books/{id}  │ 更新书籍信息（Update）            │
# │ DELETE   │ /books/{id}  │ 删除书籍（Delete）               │
# │ GET      │ /books/stats │ 统计信息（分组聚合）              │
# └──────────┴──────────────┴─────────────────────────────────┘
#
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional

from orm_01 import Book
from orm_02_session import get_db


# -----------------------------------------------------------------------------
# 第一部分：Pydantic 模型（请求/响应数据结构）
# -----------------------------------------------------------------------------
# 【为什么要用 Pydantic 模型？】
# 1. 数据验证：自动验证请求数据的类型和格式
# 2. 自动文档：FastAPI 自动生成 Swagger/OpenAPI 文档
# 3. 序列化：将 ORM 对象转换为 JSON 响应
# 4. 类型提示：提供 IDE 自动补全和类型检查

class BookCreate(BaseModel):
    """创建书籍的请求体"""
    bookname: str = Field(..., min_length=1, max_length=255, description="书名")
    author: str = Field(..., min_length=1, max_length=255, description="作者")
    price: float = Field(..., gt=0, description="价格（必须大于0）")
    publisher: str = Field(..., min_length=1, max_length=255, description="出版社")

    class Config:
        # 示例数据，显示在 Swagger 文档中
        json_schema_extra = {
            "example": {
                "bookname": "Python编程入门",
                "author": "张三",
                "price": 59.9,
                "publisher": "清华大学出版社"
            }
        }


class BookUpdate(BaseModel):
    """更新书籍的请求体（所有字段可选）"""
    bookname: Optional[str] = Field(None, max_length=255, description="书名")
    author: Optional[str] = Field(None, max_length=255, description="作者")
    price: Optional[float] = Field(None, gt=0, description="价格")
    publisher: Optional[str] = Field(None, max_length=255, description="出版社")


class BookResponse(BaseModel):
    """书籍响应体"""
    id: int
    bookname: str
    author: str
    price: float
    publisher: str

    class Config:
        # from_attributes=True 允许从 ORM 对象直接创建响应
        # 这样可以直接返回 SQLAlchemy 模型对象，FastAPI 自动转换为 JSON
        from_attributes = True


class BookListResponse(BaseModel):
    """书籍列表响应体（含分页信息）"""
    items: list[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuthorStats(BaseModel):
    """作者统计响应体"""
    author: str
    book_count: int
    avg_price: float
    max_price: float
    min_price: float


# -----------------------------------------------------------------------------
# 第二部分：创建路由
# -----------------------------------------------------------------------------
router = APIRouter(
    prefix="/books",      # 路由前缀，所有路径都以 /books 开头
    tags=["书籍管理"]      # Swagger 文档中的分组标签
)


# -----------------------------------------------------------------------------
# 第三部分：路由函数
# -----------------------------------------------------------------------------

@router.post("/", response_model=BookResponse, summary="创建书籍")
async def create_book(
    book_data: BookCreate,       # 请求体，FastAPI 自动解析 JSON
    db: AsyncSession = Depends(get_db)  # 依赖注入：获取数据库会话
):
    """
    创建新的书籍记录
    
    - **bookname**: 书名（必填）
    - **author**: 作者（必填）
    - **price**: 价格（必填，大于0）
    - **publisher**: 出版社（必填）
    """
    # 创建 ORM 对象
    book = Book(**book_data.model_dump())  # model_dump() 将 Pydantic 模型转为字典
    
    # 添加到数据库
    db.add(book)
    await db.commit()
    await db.refresh(book)  # 刷新获取数据库生成的 id 和默认值
    
    return book


@router.get("/", response_model=BookListResponse, summary="获取书籍列表")
async def list_books(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    author: Optional[str] = Query(None, description="按作者筛选"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    sort_by: str = Query("id", description="排序字段"),
    sort_order: str = Query("desc", description="排序方式：asc/desc"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取书籍列表，支持分页、筛选、排序
    
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认10，最大100）
    - **author**: 按作者筛选（可选）
    - **min_price**: 最低价格筛选（可选）
    - **max_price**: 最高价格筛选（可选）
    - **sort_by**: 排序字段（默认id）
    - **sort_order**: 排序方式（默认desc）
    """
    # 构建查询
    stmt = select(Book)
    count_stmt = select(func.count(Book.id))
    
    # 动态添加过滤条件
    if author:
        stmt = stmt.where(Book.author.like(f"%{author}%"))
        count_stmt = count_stmt.where(Book.author.like(f"%{author}%"))
    
    if min_price is not None:
        stmt = stmt.where(Book.price >= min_price)
        count_stmt = count_stmt.where(Book.price >= min_price)
    
    if max_price is not None:
        stmt = stmt.where(Book.price <= max_price)
        count_stmt = count_stmt.where(Book.price <= max_price)
    
    # 排序
    sort_column = getattr(Book, sort_by, Book.id)
    if sort_order == "desc":
        stmt = stmt.order_by(desc(sort_column))
    else:
        stmt = stmt.order_by(sort_column)
    
    # 计算总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # 分页
    import math
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    # 执行查询
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    return BookListResponse(
        items=books,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/stats", response_model=list[AuthorStats], summary="作者统计")
async def get_author_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    按作者分组统计：书籍数量、平均价格、最高价、最低价
    
    对应 SQL：
        SELECT author, COUNT(*) as book_count, AVG(price) as avg_price,
               MAX(price) as max_price, MIN(price) as min_price
        FROM book GROUP BY author ORDER BY book_count DESC
    """
    stmt = select(
        Book.author,
        func.count(Book.id).label("book_count"),
        func.round(func.avg(Book.price), 2).label("avg_price"),
        func.max(Book.price).label("max_price"),
        func.min(Book.price).label("min_price")
    ).group_by(Book.author).order_by(desc(func.count(Book.id)))
    
    result = await db.execute(stmt)
    stats = result.all()
    
    return [
        AuthorStats(
            author=row.author,
            book_count=row.book_count,
            avg_price=row.avg_price,
            max_price=row.max_price,
            min_price=row.min_price
        )
        for row in stats
    ]


@router.get("/{book_id}", response_model=BookResponse, summary="获取单个书籍")
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取书籍详情"""
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return book


@router.put("/{book_id}", response_model=BookResponse, summary="更新书籍")
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新书籍信息（部分更新）
    
    只需传入要更新的字段，未传入的字段保持不变
    """
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    # 只更新传入的字段（exclude_unset=True 排除未设置的字段）
    update_data = book_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    
    await db.commit()
    await db.refresh(book)
    
    return book


@router.delete("/{book_id}", summary="删除书籍")
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除指定书籍"""
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    await db.delete(book)
    await db.commit()
    
    return {"message": f"书籍 '{book.bookname}' 已删除"}


# -----------------------------------------------------------------------------
# 第四部分：注册路由到主应用
# -----------------------------------------------------------------------------
def register_book_router(app):
    """
    将书籍路由注册到 FastAPI 应用
    
    在 main.py 中调用：
        from orm_06_router import register_book_router
        register_book_router(app)
    """
    app.include_router(router)
