from typing import Any, Dict, List
from data_generate.tools.tool import Tool
from data_generate.tools.sql_system.context import *

class AddWhereConditions(Tool):
    @staticmethod
    def execute(
        ctx: QueryContext,
        database_path: str,
        columns: List[str],
        operators: List[FilterOperator],
        values: List[Any],
        inner_connect: LogicalOperator = "AND",
        connect_to_previous: LogicalOperator = "AND"
    ) -> QueryContext:
        if not ctx.sql_parameters.main_table:
            raise ValueError("Main table is not set. Please set a main table first.")
        if not (len(columns) == len(operators) == len(values)):
            raise ValueError("Length of columns, operators, and values must match.")

        new_group = ConditionGroup(
            columns=columns,
            operators=operators,
            values=values,
            inner_connect=inner_connect,
            connect_to_previous=connect_to_previous
        )

        if ctx.sql_parameters.where_filters is None:
            ctx.sql_parameters.where_filters = WhereFilter(groups=[])
        ctx.sql_parameters.where_filters.groups.append(new_group)

        ctx.current_sql = to_sql(ctx)
        print(ctx.current_sql)
        ctx.result = execute_sql_query(database_path, ctx.current_sql)

        return ctx

    @staticmethod
    def describe() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_where_conditions",
                "description": "Add a grouped WHERE condition with logical control.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "database_path": {"type": "string", "description": "SQLite database path."},
                        "columns": {"type": "array", "items": {"type": "string"}, "description": "List of column names."},
                        "operators": {"type": "array", "items": {"type": "string"}, "description": "List of operators."},
                        "values": {"type": "array", "items": {"type": "string"}, "description": "List of values."},
                        "inner_connect": {
                            "type": "string",
                            "enum": ["AND", "OR"],
                            "default": "AND",
                            "description": "How conditions within the group are connected."
                        },
                        "connect_to_previous": {
                            "type": "string",
                            "enum": ["AND", "OR"],
                            "default": "AND",
                            "description": "How this group connects to the previous group."
                        }
                    },
                    "required": ["database_path", "columns", "operators", "values"]
                }
            }
        }

if __name__ == '__main__':
    ctx=QueryContext(current_sql='SELECT * FROM schedules', sql_parameters=SQLParameter(select=[], main_table='schedules', join_tables=[], where_filters=None, group_by=[], having=None, order_by=[], limit=None), result=QueryResult(row_count=4467, columns=['uuid', 'start_time', 'end_time', 'mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun'], column_types=[], preview_rows=[('f2d66a4d-0c08-3b48-abf6-649fffd7ae90', -1, -1, 'false', 'false', 'false', 'false', 'false', 'false', 'false'), ('875542a2-f786-34dd-933b-84a8af1aaaba', 530, 580, 'true', 'false', 'true', 'false', 'false', 'false', 'false'), ('f41f1e4d-cb4f-3ded-b4b0-4a7c4da044e5', 660, 710, 'false', 'true', 'false', 'true', 'false', 'false', 'false'), ('46da55a4-17f7-31a1-9492-fddb5af9cf13', 800, 850, 'false', 'true', 'false', 'true', 'false', 'false', 'false'), ('8c7cd81e-4f81-357c-a40b-43f954484804', 725, 775, 'false', 'true', 'false', 'true', 'false', 'false', 'false')]), combine_type=None, combined_with=None)
    tool = AddWhereConditions()
    ctx = tool.execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        columns=["mon", "wed"],
        operators=["=", "="],
        values=["true", "true"],
        inner_connect="AND",
        connect_to_previous="AND"
    )
