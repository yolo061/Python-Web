# =============================================================================
# ORM 基础 CRUD 操作 (orm_03_crud.py)
# =============================================================================
#
# 【CRUD 是什么？】
# CRUD 是数据库操作的四个基本动作：
#   C - Create  创建（INSERT）
#   R - Read    读取（SELECT）
#   U - Update  更新（UPDATE）
#   D - Delete  删除（DELETE）
#
# 【SQLAlchemy 的两种操作方式】
# 1. ORM 方式：通过操作 Python 对象来操作数据库（本文件介绍）
#    - session.add(book)     → INSERT
#    - session.execute(stmt) → SELECT
#    - book.price = 50       → UPDATE（修改属性后 commit）
#    - session.delete(book)  → DELETE
#
# 2. Core 方式：直接构建 SQL 语句（orm_04_query.py 介绍）
#    - insert(Book).values(...)
#    - select(Book).where(...)
#    - update(Book).where(...)
#    - delete(Book).where(...)
#
# =============================================================================

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from orm_01 import Book  # 导入书籍模型
from datetime import datetime


# =============================================================================
# 一、Create（创建）
# =============================================================================
async def create_book(db: AsyncSession, book_data: dict):
    """
    创建一本书籍
    
    【ORM 插入原理】
    1. 创建模型实例（Python 对象）
    2. session.add() 将对象加入 Session 的"待提交"列表
    3. session.commit() 时，SQLAlchemy 生成 INSERT SQL 并执行
    4. 提交后，数据库自动生成的 id 会自动回填到对象的 id 属性
    
    参数：
        db: 数据库会话（通过依赖注入获取）
        book_data: 书籍数据字典，如 {"bookname": "Python入门", "author": "张三", ...}
    
    返回：
        创建成功的 Book 对象（包含数据库生成的 id）
    
    对应 SQL：
        INSERT INTO book (bookname, author, price, publisher, create_time, update_time)
        VALUES (?, ?, ?, ?, NOW(), NOW())
    """
    # 方式一：使用字典解包创建对象（推荐，简洁）
    book = Book(**book_data)
    
    # 将对象添加到 Session（此时还未执行 SQL）
    db.add(book)
    
    # 提交事务（执行 INSERT SQL）
    await db.commit()
    
    # 刷新对象，获取数据库生成的 id、create_time 等默认值
    await db.refresh(book)
    
    return book


async def create_books_batch(db: AsyncSession, books_data: list[dict]):
    """
    批量创建多本书籍
    
    【批量插入 vs 逐条插入】
    - 逐条插入：每条记录一次 commit，N 条记录 N 次网络往返
    - 批量插入：所有记录一次 commit，只需 1 次网络往返，性能更好
    
    参数：
        db: 数据库会话
        books_data: 书籍数据列表
    
    对应 SQL：
        INSERT INTO book (...) VALUES (...), (...), (...)
    """
    # 使用列表推导式创建多个对象
    books = [Book(**data) for data in books_data]
    
    # add_all 批量添加（仍然是在 commit 时才执行 SQL）
    db.add_all(books)
    
    await db.commit()
    
    # 批量刷新，获取每个对象的 id
    for book in books:
        await db.refresh(book)
    
    return books


# =============================================================================
# 二、Read（读取）
# =============================================================================
async def get_book_by_id(db: AsyncSession, book_id: int):
    """
    根据 ID 查询单本书籍
    
    【get() vs execute(select(...))】
    - session.get(Book, id): 直接通过主键查询，效率最高
    - execute(select(Book).where(Book.id == id)): 更灵活，可添加更多条件
    
    参数：
        db: 数据库会话
        book_id: 书籍 ID
    
    对应 SQL：
        SELECT * FROM book WHERE id = ?
    """
    # 方式一：使用 session.get()（主键查询推荐）
    book = await db.get(Book, book_id)
    return book

    # 方式二：使用 select 语句（更灵活）
    # stmt = select(Book).where(Book.id == book_id)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()


async def get_all_books(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    查询所有书籍（分页）
    
    【分页原理】
    - skip: 跳过前 N 条记录（偏移量）
    - limit: 最多返回 N 条记录（每页数量）
    - 第 1 页：skip=0,  limit=10 → 返回第 1-10 条
    - 第 2 页：skip=10, limit=10 → 返回第 11-20 条
    
    参数：
        db: 数据库会话
        skip: 跳过记录数（默认 0）
        limit: 返回记录数（默认 10）
    
    对应 SQL：
        SELECT * FROM book LIMIT 10 OFFSET 0
    """
    stmt = select(Book).offset(skip).limit(limit)
    result = await db.execute(stmt)
    
    # scalars() 将 Row 对象转换为模型实例
    # .all() 将结果转换为列表
    return result.scalars().all()


async def get_books_count(db: AsyncSession):
    """
    查询书籍总数
    
    对应 SQL：
        SELECT COUNT(*) FROM book
    """
    from sqlalchemy import func
    
    stmt = select(func.count(Book.id))
    result = await db.execute(stmt)
    return result.scalar()  # scalar() 返回单个值


# =============================================================================
# 三、Update（更新）
# =============================================================================
async def update_book(db: AsyncSession, book_id: int, update_data: dict):
    """
    更新书籍信息
    
    【ORM 更新的两种方式】
    方式一：直接修改对象属性（推荐，直观）
        book.price = 50
        await session.commit()
    
    方式二：使用 update 语句（适合批量更新）
        await session.execute(update(Book).where(...).values(...))
    
    参数：
        db: 数据库会话
        book_id: 要更新的书籍 ID
        update_data: 要更新的数据，如 {"price": 50.0, "publisher": "新出版社"}
    
    对应 SQL：
        UPDATE book SET price=?, publisher=?, update_time=NOW() WHERE id=?
    """
    # 先查询要更新的对象
    book = await db.get(Book, book_id)
    if not book:
        return None
    
    # 遍历更新数据，动态设置属性
    for key, value in update_data.items():
        # hasattr 检查属性是否存在，防止设置不存在的字段
        if hasattr(book, key):
            setattr(book, key, value)
    
    # 提交变更
    await db.commit()
    await db.refresh(book)
    
    return book


async def update_books_batch(db: AsyncSession, old_author: str, new_author: str):
    """
    批量更新：将某作者的所有书籍更新为新作者
    
    【批量更新 vs 逐条更新】
    - 逐条更新：先查出所有对象，逐个修改属性，N 次 UPDATE
    - 批量更新：一条 UPDATE SQL 搞定，性能更好
    
    对应 SQL：
        UPDATE book SET author=?, update_time=NOW() WHERE author=?
    """
    stmt = (
        update(Book)
        .where(Book.author == old_author)
        .values(author=new_author)
    )
    result = await db.execute(stmt)
    await db.commit()
    
    # result.rowcount 返回受影响的行数
    return result.rowcount


# =============================================================================
# 四、Delete（删除）
# =============================================================================
async def delete_book(db: AsyncSession, book_id: int):
    """
    删除单本书籍
    
    【ORM 删除原理】
    1. 先查询要删除的对象
    2. session.delete(obj) 标记对象为"待删除"
    3. commit 时执行 DELETE SQL
    
    【软删除 vs 硬删除】
    - 硬删除：直接从数据库删除记录（本例）
    - 软删除：添加 is_deleted 字段，标记为已删除（数据不真正删除）
    - 软删除更安全，数据可恢复，但查询时需要过滤已删除记录
    
    对应 SQL：
        DELETE FROM book WHERE id = ?
    """
    book = await db.get(Book, book_id)
    if not book:
        return False
    
    await db.delete(book)
    await db.commit()
    
    return True


async def delete_books_batch(db: AsyncSession, author: str):
    """
    批量删除：删除某作者的所有书籍
    
    【批量删除 vs 逐条删除】
    - 逐条删除：先查出所有对象，逐个 delete，N 次 DELETE
    - 批量删除：一条 DELETE SQL 搞定
    
    对应 SQL：
        DELETE FROM book WHERE author = ?
    """
    stmt = delete(Book).where(Book.author == author)
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount


# =============================================================================
# 五、完整示例：FastAPI 路由中使用 CRUD
# =============================================================================
"""
在 FastAPI 路由中使用这些 CRUD 函数的示例：

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from orm_02_session import get_db

router = APIRouter(prefix="/books", tags=["书籍管理"])

@router.post("/")
async def create(book_data: dict, db: AsyncSession = Depends(get_db)):
    return await create_book(db, book_data)

@router.get("/")
async def list_all(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_all_books(db, skip, limit)

@router.get("/{book_id}")
async def get_one(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book_by_id(db, book_id)
    if not book:
        return {"error": "书籍不存在"}
    return book

@router.put("/{book_id}")
async def update(book_id: int, update_data: dict, db: AsyncSession = Depends(get_db)):
    book = await update_book(db, book_id, update_data)
    if not book:
        return {"error": "书籍不存在"}
    return book

@router.delete("/{book_id}")
async def delete(book_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_book(db, book_id)
    if not success:
        return {"error": "书籍不存在"}
    return {"message": "删除成功"}
"""
