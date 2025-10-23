from typing import Any, Dict
from data_generate.tools.tool import Tool
from data_generate.tools.sql_system.context import *

class AddTableJoin(Tool):
    @staticmethod
    def execute(
        ctx: QueryContext,
        database_path: str,
        source_table: str = '',
        target_table: str = '',
        join_type: str = 'INNER',
        source_key: str = '',
        target_key: str = '',
    ) -> QueryContext:

        if not ctx.sql_parameters.main_table:
            raise ValueError("Main table is not set. Please set a main table first.")

        # 设置 JOIN 参数结构
        join_param = JoinParameter(
            source_table=source_table,
            target_table=target_table,
            join_type=join_type,
            source_key=source_key,
            target_key=target_key,
        )
        ctx.sql_parameters.join_tables.append(join_param)

        # 拼接 JOIN 子句
        for join_param in ctx.sql_parameters.join_tables:
            join_clause = f" {join_type} JOIN {target_table} ON {source_table}.{source_key}={target_table}.{target_key}"
        ctx.current_sql = to_sql(ctx)

        # 获取结果
        ctx.result = execute_sql_query(database_path,ctx.current_sql)

        return ctx

    @staticmethod
    def describe() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_join_table",
                "description": "为当前 SQL 查询添加一个 JOIN 子句。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "database_path": {
                            "type": "string",
                            "description": "SQLite 数据库路径"
                        },
                        "source_table": {
                            "type": "string",
                            "description": "当前已选中的主表"
                        },
                        "target_table": {
                            "type": "string",
                            "description": "要连接的目标表"
                        },
                        "join_type": {
                            "type": "string",
                            "enum": ["INNER", "LEFT", "RIGHT", "FULL"],
                            "description": "JOIN 类型"
                        },
                        "join_key": {
                            "type": "string",
                            "description": "连接条件，例如 'a.id = b.a_id'"
                        }
                    },
                    "required": ["database_path", "source_table", "target_table", "join_key"]
                }
            }
        }


if __name__ == '__main__':
    ctx=QueryContext(current_sql='SELECT * FROM schedules', sql_parameters=SQLParameter(select=[], main_table='schedules', join_tables=[], where_filters=None, group_by=[], having=None, order_by=[], limit=None), result=QueryResult(row_count=4467, columns=['uuid', 'start_time', 'end_time', 'mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun'], column_types=[], preview_rows=[('f2d66a4d-0c08-3b48-abf6-649fffd7ae90', -1, -1, 'false', 'false', 'false', 'false', 'false', 'false', 'false'), ('875542a2-f786-34dd-933b-84a8af1aaaba', 530, 580, 'true', 'false', 'true', 'false', 'false', 'false', 'false'), ('f41f1e4d-cb4f-3ded-b4b0-4a7c4da044e5', 660, 710, 'false', 'true', 'false', 'true', 'false', 'false', 'false'), ('46da55a4-17f7-31a1-9492-fddb5af9cf13', 800, 850, 'false', 'true', 'false', 'true', 'false', 'false', 'false'), ('8c7cd81e-4f81-357c-a40b-43f954484804', 725, 775, 'false', 'true', 'false', 'true', 'false', 'false', 'false')]), combine_type=None, combined_with=None)
    tool = AddTableJoin()
    new_ctx = tool.execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        source_table='schedules',
        target_table='sections',
        join_type='INNER',
        source_key='uuid',
        target_key='schedule_uuid'
    )

    print(new_ctx.to_dict())
