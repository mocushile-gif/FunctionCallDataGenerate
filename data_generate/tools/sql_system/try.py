from set_main_table import SetMainTable
from add_join_table import AddTableJoin
from set_select_columns import SetSelectColumns
from add_where_conditions import AddWhereConditions
from add_group_by_columns import AddGroupByColumns
from typing import Any, Callable, Dict, List, Type, Optional, Set, Union, Tuple
from data_generate.tools.tool import Tool
from data_generate.tools.sql_system.context import *

tools=[SetMainTable,AddTableJoin,SetSelectColumns,AddWhereConditions,AddGroupByColumns]
tools_map: Dict[str, Type[Tool]] = {
            tool.describe()["function"]["name"]: tool for tool in tools
        }

print(tools_map)
ctx=QueryContext()
ctx=tools_map['set_main_table'].execute(ctx,f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db','schedules')
ctx=tools_map['add_join_table'].execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        source_table='schedules',
        target_table='sections',
        join_type='INNER',
        source_key='uuid',
        target_key='schedule_uuid'
    )
ctx=tools_map['add_join_table'].execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        source_table='sections',
        target_table='course_offerings',
        join_type='INNER',
        source_key='course_offering_uuid',
        target_key='uuid'
    )
ctx = tools_map['add_where_conditions'].execute(
    ctx,
    database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
    columns=["mon", "wed"],
    operators=["=", "="],
    values=["true", "true"],
    inner_connect="AND",
    connect_to_previous="AND"
)
ctx = tools_map['set_select_columns'].execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        columns=['count(sections.uuid)','fri']
    )
ctx = tools_map['add_group_by_columns'].execute(
        ctx,
        database_path=f'{os.environ["PROJECT_DIR"]}/working_dir/file_system_new/database/uw_courses.db',
        columns=['schedules.fri']
    )
print(ctx)
