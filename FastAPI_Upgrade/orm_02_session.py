# =============================================================================
# ORM 会话管理 (orm_02_session.py)
# =============================================================================
#
# 【什么是 Session（会话）？】
# Session 是 SQLAlchemy 与数据库交互的"窗口"，它负责：
#   1. 管理数据库连接（从连接池获取/归还连接）
#   2. 跟踪对象的变化（增删改都会被记录）
#   3. 管理事务（提交/回滚）
#   4. 缓存查询结果（同一 Session 内相同主键查询返回同一对象）
#
# 【Session 的生命周期】
#   创建 Session → 执行操作 → commit(提交) 或 rollback(回滚) → 关闭 Session
#
# 【async_sessionmaker 详解】
# SQLAlchemy 2.0 推荐使用 async_sessionmaker 来创建异步 Session 工厂
# 它会自动绑定 Engine，每次调用()创建一个新的 Session 实例
#
# 【为什么每次请求需要新 Session？】
# - 线程安全：每个请求在独立的 Session 中操作，互不干扰
# - 事务隔离：一个请求的失败不会影响其他请求
# - 资源释放：请求结束后及时归还数据库连接
# =============================================================================

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from orm_01 import async_engine  # 导入之前创建的引擎

# -----------------------------------------------------------------------------
# 第一部分：创建 Session 工厂
# -----------------------------------------------------------------------------
# async_sessionmaker 是一个工厂类，调用它会创建新的 AsyncSession 实例
# 
# 参数说明：
#   - bind=async_engine: 绑定数据库引擎，Session 通过它获取连接
#   - expire_on_commit=False: commit 后对象属性不会过期
#       · True（默认）: commit 后访问对象属性会重新查询数据库
#       · False: commit 后对象属性保持原值，减少数据库查询
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)

# -----------------------------------------------------------------------------
# 第二部分：获取 Session 的方式
# -----------------------------------------------------------------------------

# 方式一：直接创建（手动管理生命周期）
# 适用于：非 FastAPI 场景、脚本、测试
async def get_session_manual():
    """
    手动创建和关闭 Session
    
    使用方式：
        session = await get_session_manual()
        try:
            # 执行数据库操作...
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    """
    return AsyncSessionFactory()


# 方式二：使用上下文管理器（推荐）
# 适用于：需要确保 Session 正确关闭的场景
async def get_session_context():
    """
    使用 async with 自动管理 Session 生命周期
    
    使用方式：
        async with get_session_context() as session:
            # 执行数据库操作...
            await session.commit()
        # 离开 with 块后 Session 自动关闭
    """
    async with AsyncSessionFactory() as session:
        yield session  # yield 使其成为异步生成器（async generator）


# 方式三：FastAPI 依赖注入（最推荐）
# 适用于：FastAPI 路由函数中使用
async def get_db():
    """
    FastAPI 依赖注入函数 —— 为每个请求提供独立的数据库 Session
    
    【依赖注入原理】
    1. FastAPI 检测到路由参数有 Depends(get_db)
    2. 自动调用 get_db() 函数
    3. 函数通过 yield 提供 Session 对象
    4. 请求处理完成后，自动执行 yield 之后的代码（清理工作）
    
    使用方式（在路由中）：
        @app.get("/books")
        async def list_books(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Book))
            return result.scalars().all()
    
    【为什么用 yield 而不是 return？】
    yield 使函数成为生成器，FastAPI 可以：
    - 在 yield 之前执行初始化代码（创建 Session）
    - 将 yield 的值注入到路由函数
    - 在请求结束后执行 yield 之后的代码（关闭 Session）
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


# -----------------------------------------------------------------------------
# 第三部分：Session 常用操作速查
# -----------------------------------------------------------------------------
"""
Session 常用方法：

┌─────────────────────────────────┬──────────────────────────────────────┐
│ 方法                             │ 说明                                  │
├─────────────────────────────────┼──────────────────────────────────────┤
│ session.add(obj)                │ 添加一个对象到 Session（INSERT）       │
│ session.add_all([obj1, obj2])   │ 批量添加多个对象                       │
│ session.delete(obj)             │ 标记对象为删除（DELETE）               │
│ await session.commit()          │ 提交事务，将所有变更写入数据库          │
│ await session.rollback()        │ 回滚事务，撤销所有未提交的变更          │
│ await session.refresh(obj)      │ 刷新对象，从数据库重新加载最新数据       │
│ await session.execute(stmt)     │ 执行 SQL 语句（SELECT/INSERT/UPDATE）  │
│ session.merge(obj)              │ 合并对象（存在则更新，不存在则插入）     │
└─────────────────────────────────┴──────────────────────────────────────┘

事务示例：
    async with AsyncSessionFactory() as session:
        async with session.begin():  # 自动管理事务
            session.add(book)
        # 离开 begin() 块自动 commit，异常时自动 rollback
"""
