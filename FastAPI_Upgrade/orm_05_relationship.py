# =============================================================================
# ORM 关联关系 (orm_05_relationship.py)
# =============================================================================
#
# 【什么是关联关系？】
# 在关系型数据库中，表与表之间存在关联关系，例如：
#   - 一个作者(Author)可以写多本书(Book) → 一对多
#   - 一本书(Book)可以有多个标签(Tag)，一个标签可以属于多本书 → 多对多
#   - 一个用户(User)有一个身份证(IDCard) → 一对一
#
# 【ORM 中如何表示关联关系？】
# 使用 relationship() 函数在模型之间建立映射关系，
# 这样可以通过 Python 对象直接访问关联数据，而不需要写 JOIN SQL。
#
# 【relationship() 常用参数】
# ┌─────────────────────┬────────────────────────────────────────────────┐
# │ 参数                 │ 说明                                            │
# ├─────────────────────┼────────────────────────────────────────────────┤
# │ "TargetModel"       │ 关联的目标模型（字符串形式，避免循环导入）        │
# │ back_populates      │ 双向关联，对方模型中对应的属性名                  │
# │ lazy                │ 加载策略：select/noload/subquery/joined/selectin │
# │ cascade             │ 级联操作：all, delete-orphan 等                  │
# │ uselist             │ True=返回列表（一对多），False=返回单个对象（一对一）│
# └─────────────────────┴────────────────────────────────────────────────┘
#
# =============================================================================

import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Table, Column
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# -----------------------------------------------------------------------------
# 基础配置
# -----------------------------------------------------------------------------
ASYNC_DATABASE_URL = "mysql+aiomysql://root:raojiarui0601@localhost:3306/FastAPI_first?charset=utf8"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    """基类，包含公共审计字段"""
    create_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now, comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now, onupdate=func.now, comment="修改时间"
    )


# =============================================================================
# 一、一对多关系（One-to-Many）
# =============================================================================
# 场景：一个作者可以写多本书
# 数据库实现：Book 表通过外键(author_id)关联 Author 表
#
# 关系图：
#   Author (一)  ──1:N──>  Book (多)
#   ┌─────────┐           ┌──────────────┐
#   │ id      │◄──────────│ author_id(FK)│
#   │ name    │           │ id           │
#   │         │           │ title        │
#   │ books[] │──┐        │ price        │
#   └─────────┘  │        └──────────────┘
#                │
#   relationship("Book") → 返回该作者的所有书籍列表
# =============================================================================

class Author(Base):
    """
    作者表
    
    【一对多关系中"一"的一方】
    - books: relationship 属性，访问该作者写的所有书籍
    - back_populates="author": 与 Book.author 建立双向关联
    """
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True, comment="作者ID")
    name: Mapped[str] = mapped_column(String(100), comment="作者姓名")
    email: Mapped[str] = mapped_column(String(200), nullable=True, comment="邮箱")

    # 【relationship 详解】
    # "Book": 关联的目标模型（用字符串避免循环导入）
    # back_populates="author": 
    #   - 在 Book 模型中有一个 author 属性指向 Author
    #   - 形成双向关联：author.books ↔ book.author
    # lazy="selectin":
    #   - 查询 Author 时自动加载关联的 Book 列表
    #   - selectin 使用单独的 SELECT 查询加载关联数据（推荐）
    #   - 其他选项：
    #     · lazy="select"（默认）: 访问时才加载（可能产生 N+1 问题）
    #     · lazy="joined": 使用 JOIN 查询一次加载（可能产生大量重复数据）
    #     · lazy="noload": 不加载关联数据
    books: Mapped[list["Book"]] = relationship(
        "Book",
        back_populates="author",
        lazy="selectin"  # 推荐：自动加载关联数据，避免 N+1 问题
    )

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"


class Book(Base):
    """
    书籍表
    
    【一对多关系中"多"的一方】
    - author_id: 外键，关联到 author 表的 id
    - author: relationship 属性，访问这本书的作者对象
    """
    __tablename__ = "book2"  # 使用不同表名避免与 orm_01.py 冲突

    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍ID")
    title: Mapped[str] = mapped_column(String(255), comment="书名")
    price: Mapped[float] = mapped_column(comment="价格")

    # 【ForeignKey 外键详解】
    # "author.id" 表示：这个列的值必须是 author 表中 id 列的值
    # 作用：
    #   1. 数据完整性：数据库会阻止插入不存在的 author_id
    #   2. 级联操作：可以设置 ON DELETE CASCADE 等
    #   3. ORM 关联：SQLAlchemy 通过外键建立表之间的关系
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.id"),  # 外键关联到 author 表的 id 列
        comment="作者ID"
    )

    # 【back_populates 双向关联】
    # 与 Author.books 形成双向关联
    # 通过 book.author 可以访问这本书的作者对象
    author: Mapped["Author"] = relationship(
        "Author",
        back_populates="books"
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"


# =============================================================================
# 二、多对多关系（Many-to-Many）
# =============================================================================
# 场景：一本书可以有多个标签，一个标签可以属于多本书
# 数据库实现：通过中间表(book_tag)关联 Book 和 Tag
#
# 关系图：
#   Book (多)  ──M:N──>  Tag (多)
#   ┌──────┐           ┌──────┐
#   │ id   │           │ id   │
#   │ title│           │ name │
#   │      │           │      │
#   │tags[]│──┐    ┌──│books │
#   └──────┘  │    │  └──────┘
#             ▼    ▼
#     ┌─────────────────┐
#     │  book_tag (中间表)│
#     │  book_id (FK)    │
#     │  tag_id  (FK)    │
#     └─────────────────┘
# =============================================================================

# 【中间表定义】
# 多对多关系需要一个中间表来存储两个表的关联关系
# 使用 Table() 定义中间表（不需要创建模型类）
book_tag_table = Table(
    "book_tag",  # 中间表名
    Base.metadata,
    Column("book_id", ForeignKey("book2.id"), primary_key=True, comment="书籍ID"),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True, comment="标签ID"),
)


class Tag(Base):
    """
    标签表
    
    【多对多关系中的一方】
    - books: relationship 属性，访问拥有该标签的所有书籍
    - secondary=book_tag_table: 指定中间表
    """
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, comment="标签ID")
    name: Mapped[str] = mapped_column(String(50), comment="标签名")

    # 【多对多 relationship 详解】
    # secondary=book_tag_table: 指定中间表
    # back_populates="tags": 与 Book.tags 形成双向关联
    books: Mapped[list["BookM2M"]] = relationship(
        "BookM2M",
        secondary=book_tag_table,  # 指定中间表
        back_populates="tags",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class BookM2M(Base):
    """
    书籍表（多对多版本）
    
    【多对多关系中的另一方】
    - tags: relationship 属性，访问这本书的所有标签
    """
    __tablename__ = "book_m2m"

    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍ID")
    title: Mapped[str] = mapped_column(String(255), comment="书名")
    price: Mapped[float] = mapped_column(comment="价格")

    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=book_tag_table,  # 使用同一个中间表
        back_populates="books",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<BookM2M(id={self.id}, title='{self.title}')>"


# =============================================================================
# 三、一对一关系（One-to-One）
# =============================================================================
# 场景：一个用户有一个用户详情
# 数据库实现：与一对多类似，但使用 uselist=False
#
# 关系图：
#   User (一)  ──1:1──>  UserDetail (一)
#   ┌──────────┐        ┌──────────────┐
#   │ id       │◄───────│ user_id (FK) │
#   │ username │        │ id           │
#   │          │        │ bio          │
#   │ detail   │──┐     │ avatar       │
#   └──────────┘  │     └──────────────┘
#                 │
#   uselist=False → 返回单个对象而不是列表
# =============================================================================

class User(Base):
    """用户表（一对一关系中的一方）"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(100), comment="用户名")

    # 【一对一的关键：uselist=False】
    # 默认情况下 relationship 返回列表（一对多）
    # 设置 uselist=False 后，返回单个对象（一对一）
    detail: Mapped["UserDetail"] = relationship(
        "UserDetail",
        back_populates="user",
        uselist=False,  # 关键：一对一必须设置为 False
        lazy="selectin",
        cascade="all, delete-orphan"  # 删除用户时，同时删除用户详情
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class UserDetail(Base):
    """用户详情表（一对一关系中的另一方）"""
    __tablename__ = "user_detail"

    id: Mapped[int] = mapped_column(primary_key=True, comment="详情ID")
    bio: Mapped[str] = mapped_column(String(500), nullable=True, comment="个人简介")
    avatar: Mapped[str] = mapped_column(String(255), nullable=True, comment="头像URL")

    # 外键关联到 user 表
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),  # ON DELETE CASCADE
        unique=True,  # unique=True 确保一对一（每个用户只能有一个详情）
        comment="用户ID"
    )

    user: Mapped["User"] = relationship("User", back_populates="detail")

    def __repr__(self):
        return f"<UserDetail(id={self.id}, user_id={self.user_id})>"


# =============================================================================
# 四、关联查询示例
# =============================================================================
async def relationship_query_examples(db):
    """
    关联关系的常见操作示例
    """
    from sqlalchemy import select

    # ---- 一对多：创建作者和书籍 ----
    author = Author(name="张三", email="zhangsan@example.com")
    db.add(author)
    await db.flush()  # flush 获取 author.id（不提交事务）

    book1 = Book(title="Python入门", price=59.9, author_id=author.id)
    book2 = Book(title="Python进阶", price=79.9, author_id=author.id)
    db.add_all([book1, book2])
    await db.commit()

    # 通过 relationship 访问关联数据
    print(author.books)   # [Book(1, 'Python入门'), Book(2, 'Python进阶')]
    print(book1.author)   # Author(1, '张三')

    # ---- 多对多：给书籍添加标签 ----
    tag_python = Tag(name="Python")
    tag编程 = Tag(name="编程")
    db.add_all([tag_python, tag编程])
    await db.flush()

    book = BookM2M(title="SQLAlchemy教程", price=49.9)
    book.tags = [tag_python, tag编程]  # 通过 relationship 直接设置关联
    db.add(book)
    await db.commit()

    print(book.tags)       # [Tag(1, 'Python'), Tag(2, '编程')]
    print(tag_python.books)  # [BookM2M(1, 'SQLAlchemy教程')]

    # ---- 关联查询：查询有"Python"标签的所有书籍 ----
    stmt = select(BookM2M).join(BookM2M.tags).where(Tag.name == "Python")
    result = await db.execute(stmt)
    python_books = result.scalars().all()

    # ---- 关联查询：查询张三写的所有书籍 ----
    stmt = select(Book).join(Book.author).where(Author.name == "张三")
    result = await db.execute(stmt)
    zhangsan_books = result.scalars().all()


# =============================================================================
# 五、建表
# =============================================================================
async def create_relationship_tables():
    """创建关联关系相关的所有表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
