from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal, Union
import sqlite3

# 支持的 JOIN 类型
JoinType = Literal["INNER", "LEFT", "RIGHT", "FULL"]

@dataclass
class JoinParameter:
    source_table: str
    target_table: str
    join_type: JoinType = "INNER"
    source_key: str = ""
    target_key: str = ""

FilterOperator = Literal["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"]
LogicalOperator = Literal["AND", "OR"]

@dataclass
class ConditionGroup:
    columns: List[str]
    operators: List[FilterOperator]
    values: List[Any]
    inner_connect: LogicalOperator = "AND"  # how columns are combined in this group
    connect_to_previous: LogicalOperator = "AND"  # 与上一组连接方式

@dataclass
class WhereFilter:
    groups: List[ConditionGroup] = field(default_factory=list)


@dataclass
class OrderBy:
    column: str
    direction: Literal["ASC", "DESC"] = "ASC"

@dataclass
class SQLParameter:
    select: List[str] = field(default_factory=list)
    main_table: str = ""
    join_tables: List[JoinParameter] = field(default_factory=list)
    where_filters: Optional[WhereFilter] = None
    group_by: List[str] = field(default_factory=list)
    having: Optional[WhereFilter] = None
    order_by: List[OrderBy] = field(default_factory=list)
    limit: Optional[int] = None

@dataclass
class QueryResult:
    row_count: int = field(default_factory=int)
    columns: List[str] = field(default_factory=list)
    column_types: List[str] = field(default_factory=list)
    preview_rows: List[Any] = field(default_factory=list)

@dataclass
class QueryContext:
    current_sql: str = ""
    sql_parameters: SQLParameter = field(default_factory=SQLParameter)
    result: QueryResult = field(default_factory=QueryResult)  # ✅ 使用新结构
    combine_type: Optional[Literal["UNION", "INTERSECT", "EXCEPT"]] = None
    combined_with: Optional['QueryContext'] = None  # 用于支持 UNION、INTERSECT 等合并查询

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_sql": self.current_sql,
            "sql_parameters": asdict(self.sql_parameters),
            "result": asdict(self.result),
            "combine_type": self.combine_type,
            "combined_with": self.combined_with.to_dict() if self.combined_with else None
        }

def to_sql(ctx: QueryContext) -> str:
    sql_parts = []

    # SELECT
    select_cols = ctx.sql_parameters.select or ['*']
    sql_parts.append("SELECT " + ", ".join(select_cols))

    # FROM (支持子查询)
    main = ctx.sql_parameters.main_table
    if isinstance(main, QueryContext):
        main_sql = f"({to_sql(main)})"
    else:
        main_sql = main
    sql_parts.append("FROM " + main_sql)

    # JOINs
    for join in ctx.sql_parameters.join_tables:
        join_target = join.target_table
        if isinstance(join_target, QueryContext):
            join_table_sql = f"({to_sql(join_target)})"
        else:
            join_table_sql = join_target
        join_clause = f"{join.join_type} JOIN {join_table_sql} ON {join.source_table}.{join.source_key} = {join_target}.{join.target_key}"
        sql_parts.append(join_clause)

    # WHERE
    if ctx.sql_parameters.where_filters:
        clause_parts = []
        where = ctx.sql_parameters.where_filters
        for i, group in enumerate(where.groups):
            # 校验一致性
            if not (len(group.columns) == len(group.operators) == len(group.values)):
                raise ValueError(f"Group {i}: columns, operators, and values must match in length.")

            # 渲染组内条件
            inner_parts = []
            for col, op, val in zip(group.columns, group.operators, group.values):
                val_str = f"'{val}'" if isinstance(val, str) else str(val)
                inner_parts.append(f"{col} {op} {val_str}")

            inner_clause = f" {group.inner_connect} ".join(inner_parts)

            # 添加前置逻辑连接符（除第一个组外）
            if i == 0:
                clause_parts.append(f"({inner_clause})")
            else:
                clause_parts.append(f"{group.connect_to_previous} ({inner_clause})")

        where_clause = "WHERE " + " ".join(clause_parts) if clause_parts else ""
        sql_parts.append(where_clause)

    # GROUP BY
    if ctx.sql_parameters.group_by:
        sql_parts.append("GROUP BY " + ", ".join(ctx.sql_parameters.group_by))

    # HAVING
    if ctx.sql_parameters.having:
        having = ctx.sql_parameters.having
        conditions = [f"{c.column} {c.operator} '{c.value}'" for c in having.conditions]
        having_clause = "HAVING "+f' {having.logical_operator} '.join(conditions)
        sql_parts.append(having_clause)

    # ORDER BY
    if ctx.sql_parameters.order_by:
        order = [f"{o.column} {o.direction}" for o in ctx.sql_parameters.order_by]
        sql_parts.append("ORDER BY " + ", ".join(order))

    # LIMIT
    if ctx.sql_parameters.limit:
        sql_parts.append(f"LIMIT {ctx.sql_parameters.limit}")

    base_sql = " ".join(sql_parts)

    # 递归组合（UNION / INTERSECT / EXCEPT）
    if ctx.combine_type and ctx.combined_with:
        combined_sql = to_sql(ctx.combined_with)
        return f"{base_sql} {ctx.combine_type} {combined_sql}"

    return base_sql

from sqlglot import parse_one
from sqlglot.expressions import Table
from typing import List

def extract_table_names(query: str) -> List[str]:
    """
    使用 sqlglot 解析 SQL 查询，返回所有参与的表名（包括 JOIN、子查询等）。
    """
    try:
        ast = parse_one(query)
        tables = ast.find_all(Table)
        return list({t.name for t in tables if t.name})
    except Exception as e:
        print(f"[extract_all_table_names] parse error: {e}")
        return []

def execute_sql_query(
    database_path: str,
    query: str,
    preview_limit: int = 5
) -> 'QueryResult':
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(query)
    results = cursor.fetchall()
    preview = results[:preview_limit]
    columns = [desc[0] for desc in cursor.description]
    row_count = len(results)

    # 自动提取表名并尝试获取列类型
    table_name = extract_table_names(query)
    column_types = None
    if table_name:
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            column_types = [row[2] for row in cursor.fetchall()]
        except Exception:
            pass  # 忽略错误，保持健壮

    conn.close()

    return QueryResult(
        row_count=row_count,
        columns=columns,
        column_types=column_types,
        preview_rows=preview,
    )
