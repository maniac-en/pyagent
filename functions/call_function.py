from typing import Any
from google.genai import types

from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python import run_python_file
from functions.write_file import write_file

functions_mapping: dict = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

WORKING_DIRECTORY: str = "./calculator"


def call_function(
    function_call_part: types.FunctionCall, verbose: bool = False
) -> types.Content:
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name: [str | None] = function_call_part.name
    function_args: dict[str, Any] | None = function_call_part.args

    if (
        function_name is not None
        and function_args is not None
        and function_name in functions_mapping.keys()
    ):
        # this means we have a valid function call decision from AI
        function_result: str = functions_mapping[function_name](
            WORKING_DIRECTORY, **function_args
        )
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
