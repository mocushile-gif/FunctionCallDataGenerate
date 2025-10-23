from typing import Any, Dict
import os
from data_generate.tools.tool import Tool
from data_generate.tools.sql_system.context import *

class SetMainTable(Tool):
    @staticmethod
    def execute(ctx: QueryContext, database_path: str, table_name: str) -> QueryContext:
        # 设置查询参数
        ctx.sql_parameters.main_table = table_name
        ctx.current_sql = to_sql(ctx)
        
        # 获取结果
        ctx.result = execute_sql_query(database_path,ctx.current_sql)
        return ctx

    @staticmethod
    def describe() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_main_table",
                "description": "选择主查询表，并初始化列结构和数据预览",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "database_path": {
                            "type": "string",
                            "description": "SQLite 数据库文件路径"
                        },
                        "table_name": {
                            "type": "string",
                            "description": "要查询的主表名称"
                        }
                    },
                    "required": ["database_path", "table_name"]
                }
            }
        }

if __name__ == '__main__':
    select=SetMainTable()
    ctx=QueryContext()
    ctx=select.execute(ctx,f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db','schedules')
    print(ctx)