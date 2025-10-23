from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, ValidationError, Field
import re

class PropertySchema(BaseModel):
    type: Optional[Union[
            Literal["string", "integer", "number", "boolean", "array", "object", "null"],
            List[Literal["string", "integer", "number", "boolean", "array", "object", "null"]]
        ]] = None
    description: Optional[str] = None
    default: Optional[Union[str, int, bool, float, dict, list]] = None
    items: Optional[Union["PropertySchema",dict]] = None # 允许items为空
    oneOf: Optional[List["PropertySchema"]] = None  # Allows "oneOf" with a string or array of strings

    # 校验 type 字段是否是允许的类型，并检查 items 的有效性
    def validate_type(self):
        if not self.type and not self.oneOf:
            raise ValueError("At least one of 'type' or 'oneOf' must be provided.")
        
        valid_types=["string", "integer", "number", "boolean", "array", "object", "null"]
        
        if self.type and type(self.type) is str:
            if self.type not in valid_types:
                raise ValueError(f"Invalid property type: {self.type}. Allowed types are: string, integer, number, boolean, array, object, null")
            
            if self.type == "array":
                if self.items!={}:
                    if not self.items:
                        raise ValueError("Array schema missing 'items' definition.")
                    # 校验 items 的类型是否合法
                    if not isinstance(self.items, PropertySchema):
                        raise ValueError(f"Invalid items schema: {self.items}")
                    self.items.validate_type()
            
        elif (self.type and type(self.type) is list):
            for single_type in self.type:
                if single_type not in valid_types:
                    raise ValueError(f"Invalid property type: {single_type}. Allowed types are: string, integer, number, boolean, array, object, null")
                if single_type=='array':
                    if self.items!={}:
                        if not self.items:
                            raise ValueError("Array schema missing 'items' definition.")
                        # 校验 items 的类型是否合法
                        if not isinstance(self.items, PropertySchema):
                            raise ValueError(f"Invalid items schema: {self.items}")
                        self.items.validate_type()
        elif self.oneOf:
            for single_type in self.oneOf:
                if single_type.type not in ["string", "integer", "number", "boolean", "array", "object", "null"]:
                    raise ValueError(f"Invalid property type: {single_type}. Allowed types are: string, integer, number, boolean, array, object, null")
                if single_type.type == "array":
                    if not single_type.items:
                        raise ValueError("Array schema missing 'items' definition.")
                    # 校验 items 的类型是否合法
                    if not isinstance(single_type.items, PropertySchema):
                        raise ValueError(f"Invalid items schema: {single_type.items}")
                    single_type.items.validate_type()
        # 如果 type 是 array，确保 items 被定义并校验其类型

        # 校验 default 的类型是否与 type 匹配
        if self.default is not None and not self._is_default_type_valid(self.default):
            raise ValueError(f"Default value '{self.default}' does not match the allowed types in '{self.type}'.")

    def _is_default_type_valid(self, default_value):
        """
        辅助方法：检查 default 值是否与 type 或 oneOf 中的类型兼容
        """
        # 如果没有指定 type 或 oneOf，返回 False
        if not self.type and not self.oneOf:
            return False

        valid_types = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }

        # 如果存在 oneOf，需要验证 default 是否与其中任何一个类型匹配
        if self.oneOf:
            for schema in self.oneOf:
                if isinstance(default_value, valid_types.get(schema.type)):
                    return True
            return False

        # 如果是 type，直接检查 default 是否匹配
        elif self.type:
            if type(self.type) is str:
                if isinstance(default_value, valid_types.get(self.type)):
                    return True
            elif type(self.type) is list:
                for schema in self.type:
                    if isinstance(default_value, valid_types.get(schema)):
                        return True  
            return False
        return False
    
class ParametersSchema(BaseModel):
    type: Literal["object"]
    properties: Dict[str, PropertySchema]
    required: List[str]

    # 校验 required 是否匹配 properties
    def validate_required(self):
        if self.required:
            invalid_keys = [key for key in self.required if key not in self.properties]
            if_duplicate = len(list(set(self.required))) !=len(self.required)
            if invalid_keys:
                raise ValueError(f"'required' contains invalid keys: {invalid_keys}")
            if if_duplicate:
                raise ValueError(f"'required' contains duplicate keys: {self.required}")

class FunctionSchema(BaseModel):
    name: str
    description: str
    parameters: ParametersSchema


FUNCTION_NAME_PATTERN = r'^[a-zA-Z0-9_\\\\.-]+$'
def validate_function_definitions(function_definitions: List[dict]):
    """
    Validate a list of function definitions against the OpenAI schema.

    Parameters:
        function_definitions (List[dict]): A list of function definitions in JSON-like format.

    Returns:
        List[dict]: Validation results with success or detailed error messages.
    """
    results = []
    for i, func_def in enumerate(function_definitions):
        try:
            # Validate function name against the regex pattern
            function_name = func_def["name"]
            if not re.match(FUNCTION_NAME_PATTERN, function_name):
                    raise Exception(f"Invalid function name '{function_name}'. It must match the pattern: {FUNCTION_NAME_PATTERN}")

            # 尝试校验该函数定义
            function = FunctionSchema(**func_def)
            # 校验类型和 required 匹配逻辑
            for prop_name, prop in function.parameters.properties.items():
                prop.validate_type()
            function.parameters.validate_required()

            # results.append({"function": function.name, "valid": True, "error": None})
        except ValidationError as ve:
            results.append({"function": func_def.get("name", f"Function {i + 1}"), "valid": False, "error": str(ve)})
        except Exception as e:
            results.append({"function": func_def.get("name", f"Function {i + 1}"), "valid": False, "error": str(e)})

    return results


if __name__ == "__main__":
    # 示例 JSON 数据
    from load_tool_defines import load_tool_defines
    executable_tools=load_tool_defines(f'{os.environ["PROJECT_DIR"]}/tools/defines/',True)
    function_definitions = list(executable_tools.values())
    # 批量校验
    validation_results = validate_function_definitions(function_definitions)

    # 打印结果
    for result in validation_results:
        print(f"Function: {result['function']}")
        print(f"Valid: {result['valid']}")
        print(f"Error: {result['error']}")
        print("-" * 50)
    print(len(validation_results))
