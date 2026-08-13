# =============================================================================
# ORM 高级查询操作 (orm_04_query.py)
# =============================================================================
#
# 【本文件涵盖的查询技巧】
# 1. 条件查询（where）       → 精确匹配、模糊查询、范围查询
# 2. 排序（order_by）        → 升序、降序、多字段排序
# 3. 分组（group_by）        → 按字段分组统计
# 4. 聚合函数（func）         → COUNT、SUM、AVG、MAX、MIN
# 5. 分页（offset/limit）    → 偏移量分页
# 6. 子查询（subquery）      → 嵌套查询
# 7. 联表查询（join）        → 多表关联查询
# 8. 去重（distinct）        → 查询不重复的值
#
# 【SQLAlchemy 查询构建流程】
#   select(Model)          → 选择要查询的表
#   .where(条件)            → 过滤条件
#   .order_by(排序)         → 排序规则
#   .group_by(分组字段)     → 分组依据
#   .having(分组后条件)     → 分组后的过滤
#   .offset(n).limit(m)    → 分页
#   → 最终通过 db.execute(stmt) 执行
# =============================================================================

from sqlalchemy import select, func, and_, or_, desc, asc, distinct, text
from sqlalchemy.ext.asyncio import AsyncSession
from orm_01 import Book


# =============================================================================
# 一、条件查询（WHERE）
# =============================================================================
async def query_where_examples(db: AsyncSession):
    """
    条件查询示例集合
    
    【常见 WHERE 条件操作符】
    ┌────────────────────┬──────────────────────────┬─────────────────────┐
    │ Python 表达式       │ 含义                      │ SQL 等价             │
    ├────────────────────┼──────────────────────────┼─────────────────────┤
    │ Book.id == 1       │ 等于                      │ id = 1              │
    │ Book.id != 1       │ 不等于                    │ id != 1             │
    │ Book.price > 50    │ 大于                      │ price > 50          │
    │ Book.price < 50    │ 小于                      │ price < 50          │
    │ Book.price >= 50   │ 大于等于                  │ price >= 50         │
    │ Book.price <= 50   │ 小于等于                  │ price <= 50         │
    │ Book.id.in_([1,2]) │ 在列表中                  │ id IN (1, 2)        │
    │ Book.id.not_in(..) │ 不在列表中                │ id NOT IN (...)     │
    │ Book.name.like(..) │ 模糊匹配（% 通配符）      │ name LIKE '%xx%'    │
    │ Book.name.ilike(.) │ 模糊匹配（不区分大小写）   │ name ILIKE '%xx%'   │
    │ Book.price.between │ 范围查询                  │ price BETWEEN 10 AND│
    │   (10, 100)        │                          │   100               │
    └────────────────────┴──────────────────────────┴─────────────────────┘
    """
    
    # 示例 1：精确查询 —— 查询作者为"张三"的书籍
    # 对应 SQL: SELECT * FROM book WHERE author = '张三'
    stmt = select(Book).where(Book.author == "张三")
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 2：模糊查询 —— 查询书名包含"Python"的书籍
    # 对应 SQL: SELECT * FROM book WHERE bookname LIKE '%Python%'
    stmt = select(Book).where(Book.bookname.like("%Python%"))
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 3：多条件 AND 查询 —— 查询作者为"张三"且价格大于 50 的书籍
    # 对应 SQL: SELECT * FROM book WHERE author = '张三' AND price > 50
    stmt = select(Book).where(
        and_(
            Book.author == "张三",
            Book.price > 50
        )
    )
    # 简写方式（多个 where 默认是 AND 关系）：
    # stmt = select(Book).where(Book.author == "张三").where(Book.price > 50)
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 4：OR 条件查询 —— 查询作者为"张三"或"李四"的书籍
    # 对应 SQL: SELECT * FROM book WHERE author = '张三' OR author = '李四'
    stmt = select(Book).where(
        or_(
            Book.author == "张三",
            Book.author == "李四"
        )
    )
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 5：IN 查询 —— 查询指定 ID 列表中的书籍
    # 对应 SQL: SELECT * FROM book WHERE id IN (1, 3, 5, 7)
    stmt = select(Book).where(Book.id.in_([1, 3, 5, 7]))
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 6：范围查询 —— 查询价格在 30 到 100 之间的书籍
    # 对应 SQL: SELECT * FROM book WHERE price BETWEEN 30 AND 100
    stmt = select(Book).where(Book.price.between(30, 100))
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    return books


# =============================================================================
# 二、排序（ORDER BY）
# =============================================================================
async def query_order_examples(db: AsyncSession):
    """
    排序查询示例
    
    【排序方式】
    - asc(字段)  → 升序（从小到大，A→Z）（默认）
    - desc(字段) → 降序（从大到小，Z→A）
    - 可以按多个字段排序，先按第一个字段排，相同再按第二个排
    """
    
    # 示例 1：按价格升序排列
    # 对应 SQL: SELECT * FROM book ORDER BY price ASC
    stmt = select(Book).order_by(asc(Book.price))
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 2：按价格降序排列
    # 对应 SQL: SELECT * FROM book ORDER BY price DESC
    stmt = select(Book).order_by(desc(Book.price))
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    # 示例 3：多字段排序 —— 先按作者升序，再按价格降序
    # 对应 SQL: SELECT * FROM book ORDER BY author ASC, price DESC
    stmt = select(Book).order_by(asc(Book.author), desc(Book.price))
    result = await db.execute(stmt)
    books = result.scalars().all()
    
    return books


# =============================================================================
# 三、分组与聚合（GROUP BY + 聚合函数）
# =============================================================================
async def query_group_examples(db: AsyncSession):
    """
    分组查询示例 —— GROUP BY 是 SQL 中非常重要的功能
    
    【什么是分组？】
    将表中具有相同字段值的行归为一组，然后对每组进行统计计算。
    
    例如：按作者分组，统计每个作者写了多少本书、平均价格是多少。
    
    【常用聚合函数】
    ┌─────────────────┬──────────────────────────────────────┐
    │ 函数             │ 说明                                  │
    ├─────────────────┼──────────────────────────────────────┤
    │ func.count()    │ 计数（统计行数）                       │
    │ func.sum()      │ 求和                                  │
    │ func.avg()      │ 求平均值                               │
    │ func.max()      │ 求最大值                               │
    │ func.min()      │ 求最小值                               │
    │ func.group_concat() │ 将分组内的值连接成字符串（MySQL）   │
    └─────────────────┴──────────────────────────────────────┘
    
    【分组查询的关键规则】
    SELECT 中出现的字段，要么在 GROUP BY 中，要么是聚合函数
    正确：SELECT author, COUNT(*) FROM book GROUP BY author
    错误：SELECT author, bookname, COUNT(*) FROM book GROUP BY author
          （bookname 既不在 GROUP BY 中，也不是聚合函数）
    """
    
    # 示例 1：按作者分组，统计每个作者的书籍数量
    # 对应 SQL: SELECT author, COUNT(*) AS book_count FROM book GROUP BY author
    stmt = select(
        Book.author,                          # 分组字段
        func.count(Book.id).label("book_count")  # 聚合函数，label 给结果列起别名
    ).group_by(Book.author)
    result = await db.execute(stmt)
    # result.all() 返回的是 Row 对象列表，每个 Row 包含 (author, book_count)
    stats = result.all()
    # stats 示例: [("张三", 5), ("李四", 3), ("王五", 8)]
    
    # 示例 2：按作者分组，统计书籍数量、平均价格、最高价格、最低价格
    # 对应 SQL: 
    #   SELECT author, COUNT(*) AS count, AVG(price) AS avg_price,
    #          MAX(price) AS max_price, MIN(price) AS min_price
    #   FROM book GROUP BY author
    stmt = select(
        Book.author,
        func.count(Book.id).label("count"),
        func.avg(Book.price).label("avg_price"),
        func.max(Book.price).label("max_price"),
        func.min(Book.price).label("min_price")
    ).group_by(Book.author)
    result = await db.execute(stmt)
    stats = result.all()
    
    # 示例 3：分组 + 条件过滤（HAVING）
    # HAVING 是对分组后的结果进行过滤（WHERE 是对分组前的行过滤）
    # 对应 SQL: 
    #   SELECT author, COUNT(*) AS book_count
    #   FROM book GROUP BY author
    #   HAVING COUNT(*) > 3
    #
    # 含义：找出写了超过 3 本书的作者
    stmt = select(
        Book.author,
        func.count(Book.id).label("book_count")
    ).group_by(Book.author).having(func.count(Book.id) > 3)
    result = await db.execute(stmt)
    stats = result.all()
    
    # 示例 4：按出版社分组，计算每个出版社的总销售额
    # 对应 SQL:
    #   SELECT publisher, SUM(price) AS total_price, COUNT(*) AS book_count
    #   FROM book GROUP BY publisher
    #   ORDER BY total_price DESC
    stmt = select(
        Book.publisher,
        func.sum(Book.price).label("total_price"),
        func.count(Book.id).label("book_count")
    ).group_by(Book.publisher).order_by(desc(func.sum(Book.price)))
    result = await db.execute(stmt)
    stats = result.all()
    
    return stats


# =============================================================================
# 四、去重查询（DISTINCT）
# =============================================================================
async def query_distinct_examples(db: AsyncSession):
    """
    去重查询示例
    
    【DISTINCT vs GROUP BY 的区别】
    - DISTINCT: 简单去重，不支持聚合函数
    - GROUP BY: 分组统计，支持聚合函数
    - 如果只是去重，用 DISTINCT 更简洁
    """
    
    # 示例 1：查询所有不重复的作者名
    # 对应 SQL: SELECT DISTINCT author FROM book
    stmt = select(distinct(Book.author))
    result = await db.execute(stmt)
    authors = result.scalars().all()
    
    # 示例 2：查询所有不重复的出版社
    # 对应 SQL: SELECT DISTINCT publisher FROM book
    stmt = select(Book.publisher).distinct()
    result = await db.execute(stmt)
    publishers = result.scalars().all()
    
    return authors, publishers


# =============================================================================
# 五、子查询（Subquery）
# =============================================================================
async def query_subquery_examples(db: AsyncSession):
    """
    子查询示例 —— 在一个查询中嵌套另一个查询
    
    【子查询的使用场景】
    1. 查询价格高于平均价的书籍
    2. 查询每个作者最贵的书
    3. 查询有订单的用户（通过子查询关联）
    """
    
    # 示例：查询价格高于平均价格的书籍
    # 对应 SQL:
    #   SELECT * FROM book
    #   WHERE price > (SELECT AVG(price) FROM book)
    
    # 步骤 1：构建子查询（计算平均价格）
    avg_subquery = select(func.avg(Book.price)).scalar_subquery()
    
    # 步骤 2：在主查询中使用子查询
    stmt = select(Book).where(Book.price > avg_subquery)
    result = await db.execute(stmt)
    expensive_books = result.scalars().all()
    
    return expensive_books


# =============================================================================
# 六、原生 SQL 查询
# =============================================================================
async def query_raw_sql_examples(db: AsyncSession):
    """
    原生 SQL 查询 —— 当 ORM 无法满足复杂需求时使用
    
    【什么时候用原生 SQL？】
    - 复杂的统计查询，ORM 难以表达
    - 数据库特有的功能（如 MySQL 的 GROUP_CONCAT）
    - 性能关键的查询，需要手动优化 SQL
    
    【注意】
    原生 SQL 可能存在 SQL 注入风险，务必使用参数化查询
    """
    
    # 方式一：使用 text() 执行原生 SQL（推荐）
    # :author 是参数占位符，通过 params 传入
    stmt = text("SELECT * FROM book WHERE author = :author AND price > :price")
    result = await db.execute(stmt, {"author": "张三", "price": 50})
    books = result.fetchall()
    
    # 方式二：直接传入 SQL 字符串
    result = await db.execute(
        text("SELECT author, COUNT(*) as cnt FROM book GROUP BY author"),
    )
    stats = result.fetchall()
    
    return books, stats


# =============================================================================
# 七、分页查询封装
# =============================================================================
async def paginate_query(
    db: AsyncSession,
    model,
    page: int = 1,
    page_size: int = 10,
    filters: list = None,
    order_by=None
):
    """
    通用分页查询函数
    
    【分页参数计算】
    - page: 当前页码（从 1 开始）
    - page_size: 每页记录数
    - offset = (page - 1) * page_size  → 跳过的记录数
    
    参数：
        db: 数据库会话
        model: ORM 模型类
        page: 页码（默认第 1 页）
        page_size: 每页数量（默认 10 条）
        filters: 过滤条件列表，如 [Book.author == "张三"]
        order_by: 排序字段，如 desc(Book.price)
    
    返回：
        {
            "items": [...],       # 当前页数据
            "total": 100,         # 总记录数
            "page": 1,            # 当前页码
            "page_size": 10,      # 每页数量
            "total_pages": 10     # 总页数
        }
    """
    # 构建基础查询
    stmt = select(model)
    count_stmt = select(func.count(model.id))
    
    # 添加过滤条件
    if filters:
        for filter_condition in filters:
            stmt = stmt.where(filter_condition)
            count_stmt = count_stmt.where(filter_condition)
    
    # 添加排序
    if order_by is not None:
        stmt = stmt.order_by(order_by)
    
    # 计算总记录数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # 计算总页数（向上取整）
    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    # 应用分页
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    # 执行查询
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
