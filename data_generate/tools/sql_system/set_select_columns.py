from typing import Any, Dict, List
import sqlite3
from data_generate.tools.tool import Tool
from data_generate.tools.sql_system.context import *

class SetSelectColumns(Tool):
    @staticmethod
    def execute(ctx: QueryContext, database_path: str, columns: List[str]) -> QueryContext:
        if not ctx.sql_parameters.main_table:
            raise ValueError("Main table is not set. Please set a main table first.")
        
        # 设置 SELECT 子句
        ctx.sql_parameters.select = columns
        ctx.current_sql = to_sql(ctx)

        # 获取结果
        ctx.result = execute_sql_query(database_path,ctx.current_sql)
        return ctx

    @staticmethod
    def describe() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_select_columns",
                "description": (
                    "Set the SELECT columns and preview top 5 rows. "
                    "If join tables have duplicate column names, use 'table.column' to avoid ambiguity."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "database_path": {
                            "type": "string",
                            "description": "Path to the SQLite database file."
                        },
                        "columns": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": (
                                "List of column names to select. "
                                "Use 'table.column' if there are duplicates across joined tables."
                            )
                        }
                    },
                    "required": ["database_path", "columns"]
                }
            }
        }


if __name__ == '__main__':
    tool = SetSelectColumns()
    ctx = QueryContext()
    ctx.sql_parameters.main_table = 'schedules'

    ctx = tool.execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        columns=['uuid', 'start_time', 'mon']
    )

    print(ctx)
