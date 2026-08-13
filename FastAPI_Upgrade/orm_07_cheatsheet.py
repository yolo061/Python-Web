# =============================================================================
# ORM 操作速查手册 (orm_07_cheatsheet.py)
# =============================================================================
#
# 本文件是 SQLAlchemy ORM 常用操作的快速参考，方便日常开发查阅。
#
# =============================================================================


# =============================================================================
# 一、模型定义速查
# =============================================================================
"""
1. 基础模型定义：

    class User(Base):
        __tablename__ = "user"
        
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))
        age: Mapped[int] = mapped_column(Integer, default=0)
        email: Mapped[str] = mapped_column(String(200), nullable=True)

2. 常用列类型：

    Python 类型    →  SQLAlchemy 类型       →  数据库类型
    int            →  Integer              →  INT
    str            →  String(长度)         →  VARCHAR(长度)
    str            →  Text                 →  TEXT
    float          →  Float                →  FLOAT
    bool           →  Boolean              →  TINYINT(1)
    datetime       →  DateTime             →  DATETIME
    date           →  Date                 →  DATE
    Decimal        →  Numeric(p, s)        →  DECIMAL(p, s)

3. 常用列参数：

    primary_key=True     → 主键
    autoincrement=True   → 自动递增（主键默认开启）
    nullable=False       → NOT NULL（不允许为空）
    unique=True          → 唯一约束
    index=True           → 创建索引
    default=值           → Python 层面的默认值
    server_default=值    → 数据库层面的默认值
    comment="说明"       → 列注释
"""


# =============================================================================
# 二、CRUD 操作速查
# =============================================================================
"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ CREATE（创建）                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ # 创建单条                                                                   │
│ user = User(name="张三", age=25)                                            │
│ db.add(user)                                                                │
│ await db.commit()                                                           │
│ await db.refresh(user)  # 获取数据库生成的 id                                │
│                                                                             │
│ # 批量创建                                                                   │
│ users = [User(name="A", age=20), User(name="B", age=30)]                    │
│ db.add_all(users)                                                           │
│ await db.commit()                                                           │
│                                                                             │
│ # 使用字典创建                                                               │
│ data = {"name": "张三", "age": 25}                                          │
│ user = User(**data)                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ READ（读取）                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ # 主键查询（最快）                                                           │
│ user = await db.get(User, 1)                                                │
│                                                                             │
│ # 条件查询                                                                   │
│ stmt = select(User).where(User.name == "张三")                              │
│ result = await db.execute(stmt)                                             │
│ user = result.scalar_one_or_none()  # 单条或 None                           │
│ users = result.scalars().all()      # 列表                                  │
│                                                                             │
│ # 查询所有                                                                   │
│ stmt = select(User)                                                         │
│ result = await db.execute(stmt)                                             │
│ users = result.scalars().all()                                              │
│                                                                             │
│ # 分页查询                                                                   │
│ stmt = select(User).offset(0).limit(10)  # 第 1 页，每页 10 条               │
│                                                                             │
│ # 排序                                                                       │
│ from sqlalchemy import asc, desc                                            │
│ stmt = select(User).order_by(desc(User.age))                                │
│                                                                             │
│ # 只查特定列                                                                 │
│ stmt = select(User.name, User.age)                                          │
│ result = await db.execute(stmt)                                             │
│ rows = result.all()  # 每个 Row 是 (name, age) 元组                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ UPDATE（更新）                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ # 方式一：修改对象属性（推荐）                                                │
│ user = await db.get(User, 1)                                                │
│ user.name = "新名字"                                                        │
│ user.age = 30                                                               │
│ await db.commit()                                                           │
│                                                                             │
│ # 方式二：批量更新（性能更好）                                                │
│ from sqlalchemy import update                                               │
│ stmt = update(User).where(User.age < 18).values(age=18)                     │
│ await db.execute(stmt)                                                      │
│ await db.commit()                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DELETE（删除）                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ # 删除单条                                                                   │
│ user = await db.get(User, 1)                                                │
│ await db.delete(user)                                                       │
│ await db.commit()                                                           │
│                                                                             │
│ # 批量删除                                                                   │
│ from sqlalchemy import delete                                               │
│ stmt = delete(User).where(User.age < 0)                                     │
│ await db.execute(stmt)                                                      │
│ await db.commit()                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""


# =============================================================================
# 三、WHERE 条件速查
# =============================================================================
"""
from sqlalchemy import and_, or_, not_

# 等于
User.name == "张三"

# 不等于
User.name != "张三"

# 大于/小于/大于等于/小于等于
User.age > 18
User.age < 60
User.age >= 18
User.age <= 60

# IN 查询
User.id.in_([1, 2, 3])

# NOT IN 查询
User.id.not_in([1, 2, 3])

# LIKE 模糊查询
User.name.like("%张%")         # 区分大小写
User.name.ilike("%张%")        # 不区分大小写

# BETWEEN 范围查询
User.age.between(18, 60)

# IS NULL / IS NOT NULL
User.email.is_(None)           # email IS NULL
User.email.is_not(None)        # email IS NOT NULL

# AND 条件
and_(User.age > 18, User.name == "张三")
# 或者链式调用（默认 AND）
select(User).where(User.age > 18).where(User.name == "张三")

# OR 条件
or_(User.name == "张三", User.name == "李四")

# NOT 条件
not_(User.age < 18)
"""


# =============================================================================
# 四、聚合函数速查
# =============================================================================
"""
from sqlalchemy import func

# 计数
func.count(User.id)            → COUNT(user.id)
func.count("*")                → COUNT(*)

# 求和
func.sum(Order.amount)         → SUM(order.amount)

# 平均值
func.avg(User.age)             → AVG(user.age)
func.round(func.avg(...), 2)   → ROUND(AVG(...), 2)  保留 2 位小数

# 最大值 / 最小值
func.max(User.age)             → MAX(user.age)
func.min(User.age)             → MIN(user.age)

# 字符串拼接（MySQL）
func.group_concat(User.name)   → GROUP_CONCAT(user.name)

# 使用示例
stmt = select(
    User.department,
    func.count(User.id).label("count"),
    func.avg(User.age).label("avg_age")
).group_by(User.department)

# HAVING 过滤
stmt = stmt.having(func.count(User.id) > 5)
"""


# =============================================================================
# 五、关联关系速查
# =============================================================================
"""
# 一对多（Author → Book）
class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")

# 一对一（User → UserDetail）
class User(Base):
    detail: Mapped["UserDetail"] = relationship(
        "UserDetail", back_populates="user", uselist=False
    )

class UserDetail(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="detail")

# 多对多（Book ↔ Tag）
book_tag = Table("book_tag", Base.metadata,
    Column("book_id", ForeignKey("book.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Book(Base):
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=book_tag, back_populates="books"
    )

class Tag(Base):
    books: Mapped[list["Book"]] = relationship(
        "Book", secondary=book_tag, back_populates="tags"
    )
"""


# =============================================================================
# 六、常见问题与注意事项
# =============================================================================
"""
1. N+1 查询问题：
   - 问题：查询 N 个对象，每个对象的关联数据需要额外查询，总共 N+1 次查询
   - 解决：使用 lazy="selectin" 或 joinedload 预加载关联数据
   
   # 预加载示例
   from sqlalchemy.orm import selectinload
   stmt = select(Author).options(selectinload(Author.books))

2. Session 生命周期：
   - 每个请求一个 Session（通过依赖注入）
   - 请求结束自动关闭 Session
   - 不要在多个请求间共享 Session

3. 事务管理：
   - 默认每次 commit 都是独立事务
   - 使用 async with session.begin() 管理复杂事务
   - 异常时自动 rollback

4. 性能优化：
   - 批量操作用 add_all / update / delete 语句
   - 只查需要的列：select(User.name, User.age)
   - 合理使用索引：index=True
   - 分页查询避免 offset 过大（大 offset 性能差）

5. 安全注意：
   - 不要拼接 SQL 字符串（SQL 注入风险）
   - 使用参数化查询：text("... WHERE id = :id"), {"id": 1}
   - 敏感数据不要硬编码（用环境变量）
"""
