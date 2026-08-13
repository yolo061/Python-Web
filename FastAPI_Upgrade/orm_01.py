# =============================================================================
# ORM 基础配置文件 (orm_01.py)
# =============================================================================
#
# 【什么是 ORM？】
# ORM (Object-Relational Mapping，对象关系映射) 是一种编程技术，它将数据库中的
# 表(Table)映射为 Python 中的类(Class)，将表中的行(Row)映射为类的实例(Instance)，
# 将表中的列(Column)映射为类的属性(Attribute)。
#
# 简单来说：不用写 SQL 语句，直接用 Python 代码操作数据库。
#
# 【SQLAlchemy 是什么？】
# SQLAlchemy 是 Python 中最流行的 ORM 框架，它提供了：
#   1. ORM 功能：将 Python 类映射到数据库表
#   2. SQL 表达式：可以构建复杂的 SQL 查询
#   3. 数据库连接池：管理数据库连接，提高性能
#   4. 事务管理：确保数据操作的原子性
#
# 【为什么用异步(Async)？】
# FastAPI 是异步框架，使用异步 ORM 可以：
#   - 在等待数据库响应时处理其他请求（不阻塞）
#   - 提高并发性能，适合高流量场景
#   - 配合 FastAPI 的 async/await 语法使用
#
# 【本文件的作用】
#   1. 创建数据库连接引擎（Engine）
#   2. 定义 ORM 模型基类（Base）
#   3. 定义具体的数据库表模型（如 Book）
#   4. 提供建表函数，在应用启动时自动创建表
# =============================================================================

# -----------------------------------------------------------------------------
# 第一部分：导入依赖
# -----------------------------------------------------------------------------
import datetime
from fastapi import FastAPI
from sqlalchemy import DateTime, func, String, Float  # SQLAlchemy 核心类型和函数
# create_async_engine: 创建异步数据库引擎，负责管理数据库连接
from sqlalchemy.ext.asyncio import create_async_engine
# DeclarativeBase: ORM 模型的基类，所有模型都要继承它
# Mapped: 类型注解，声明该属性映射到数据库表的某个列
from sqlalchemy.orm import DeclarativeBase, Mapped
# mapped_column: 用于定义列的详细属性（主键、类型、默认值等）
from sqlalchemy.testing.schema import mapped_column

# -----------------------------------------------------------------------------
# 第二部分：数据库连接配置
# -----------------------------------------------------------------------------
# 数据库连接 URL 格式：
#   mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8
#
#   - mysql+aiomysql: 使用 aiomysql 驱动（异步 MySQL 驱动）
#   - 其他常见驱动：
#     · mysql+pymysql    → 同步 MySQL 驱动
#     · sqlite+aiosqlite → 异步 SQLite 驱动
#     · postgresql+asyncpg → 异步 PostgreSQL 驱动
#
# ⚠️ 安全提示：生产环境不要硬编码密码，应使用环境变量或配置文件
ASYNC_DATABASE_URL = "mysql+aiomysql://root:raojiarui0601@localhost:3306/FastAPI_first?charset=utf8"

# 创建异步数据库引擎（Engine）
# Engine 是 SQLAlchemy 与数据库通信的核心对象
async_engine: create_async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,           # echo=True 会在控制台输出生成的 SQL 语句（调试用，生产环境关闭）
    pool_size=10,        # 连接池大小：保持 10 个持久连接，避免频繁创建/销毁连接
    max_overflow=20      # 溢出连接数：当连接池满时，最多再创建 20 个临时连接
    # 总最大连接数 = pool_size + max_overflow = 30
)

# -----------------------------------------------------------------------------
# 第三部分：定义 ORM 模型基类
# -----------------------------------------------------------------------------
# 【DeclarativeBase 详解】
# DeclarativeBase 是 SQLAlchemy 2.0 推荐的声明式基类写法。
# 所有数据表模型都继承自这个基类，它提供：
#   - metadata: 存储所有表的元数据信息（表名、列、约束等）
#   - 自动生成 SQL CREATE TABLE 语句的能力
#
# 【为什么要有基类？】
# 1. 代码复用：公共字段（如 create_time、update_time）只需定义一次
# 2. 统一管理：所有模型共享同一个 metadata，方便批量建表
# 3. 规范约束：确保所有表都有统一的审计字段
class Base(DeclarativeBase):
    """
    ORM 模型基类 —— 所有表模型都继承此类
    包含公共字段：创建时间、更新时间
    """
    # 【Mapped 类型注解详解】
    # Mapped[datetime] 表示这个属性映射到数据库的一个 datetime 类型的列
    # SQLAlchemy 2.0 使用 Mapped 来提供更好的类型提示和 IDE 支持
    #
    # 【mapped_column() 参数详解】
    #   - DateTime: 列的数据库类型
    #   - insert_default=func.now: 插入时的默认值（SQL 的 NOW() 函数）
    #   - onupdate=func.now: 更新记录时自动设置为当前时间
    #   - comment: 列的注释说明

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now,   # 插入时自动填充当前时间
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now,   # 插入时自动填充当前时间
        onupdate=func.now,         # 每次更新记录时自动刷新为当前时间
        comment="修改时间"
    )

# -----------------------------------------------------------------------------
# 第四部分：定义具体的表模型
# -----------------------------------------------------------------------------
# 【如何定义一个表模型？】
# 1. 继承 Base 基类
# 2. 设置 __tablename__ 指定对应的数据库表名
# 3. 使用 Mapped[type] + mapped_column() 定义每一列
# 4. 主键列必须设置 primary_key=True
#
# 【常用列类型对照】
#   Python 类型    │  SQLAlchemy 类型      │  MySQL 类型
#   ──────────────┼──────────────────────┼──────────────
#   int           │  Integer             │  INT
#   str           │  String(长度)        │  VARCHAR(长度)
#   float         │  Float               │  FLOAT/DOUBLE
#   bool          │  Boolean             │  TINYINT(1)
#   datetime      │  DateTime            │  DATETIME
#   text          │  Text                │  TEXT
#   Decimal       │  Numeric(precision)  │  DECIMAL
#
class Book(Base):
    """
    书籍表模型 —— 对应数据库中的 book 表
    字段：id、书名、作者、价格、出版社
    """
    # __tablename__ 指定该模型对应的数据库表名
    __tablename__ = "book"

    # 主键列：id
    # primary_key=True 表示这是主键，数据库会自动递增
    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍id")

    # String(255) 表示 VARCHAR(255)，最多存储 255 个字符
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")

    # Float 表示浮点数类型，适合存储价格
    # 注意：如果需要精确计算（如金融），建议使用 Numeric/Decimal 类型
    price: Mapped[float] = mapped_column(Float, comment="价格")

    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")

# -----------------------------------------------------------------------------
# 第五部分：建表与应用注册
# -----------------------------------------------------------------------------
async def create_tables():
    """
    在应用启动时自动创建所有表
    
    【工作原理】
    1. async with async_engine.begin() → 从连接池获取连接，开始事务
    2. conn.run_sync(Base.metadata.create_all) → 在同步上下文中执行建表
    3. Base.metadata 包含了所有继承自 Base 的模型的表结构信息
    4. create_all() 会检查表是否已存在，不存在才创建（不会重复创建）
    
    【为什么用 run_sync？】
    SQLAlchemy 的 DDL（建表语句）目前没有完全异步化，
    所以需要用 run_sync() 在异步上下文中执行同步操作
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def register_orm(app: FastAPI):
    """
    将 ORM 建表逻辑注册到 FastAPI 的启动事件中
    
    【FastAPI 生命周期事件】
    - startup: 应用启动时执行（适合初始化数据库、建表等）
    - shutdown: 应用关闭时执行（适合清理资源、关闭连接等）
    
    使用 @app.on_event("startup") 装饰器注册启动事件
    """
    @app.on_event("startup")
    async def startup_event():
        await create_tables()