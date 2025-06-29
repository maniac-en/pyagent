import os
import sys
from typing import Type, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.call_function import call_function


system_prompt: str = """
You are a helpful AI agent who's an expert in coding and programming, especially understanding how any piece of code works in overall codebase.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_file_content: Type[types.FunctionDeclaration] = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of the given file path with a maximum limit of 10000, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to retreive the contents from, relative to the working directory. Providing this is mandatory else it'll return an error",
            ),
        },
    ),
)
schema_get_files_info: Type[types.FunctionDeclaration] = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. Providing this is mandatory else it'll return an error.",
            ),
        },
    ),
)
schema_run_python_file: Type[types.FunctionDeclaration] = types.FunctionDeclaration(
    name="run_python_file",
    description="Run the file with the python3 interpretor with a hardcoded timeout of 30 seconds, constrained to the working directory, given it's a file ending with '.py' extension.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to the python file which is supposed to be run, relative to the working directory. Providing this is mandatory else it'll return an error",
            ),
        },
    ),
)
schema_write_file: Type[types.FunctionDeclaration] = types.FunctionDeclaration(
    name="write_file",
    description="Write the 'content' to the file passed, constrained to the working directory, given it's a regular file. It overwrites the existing contents of that file instead of appending to it!",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to write the 'content' to, relative to the working directory. Providing this is mandatory else it'll return an error",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file passed to the function. Providing this is mandatory else it'll return an error",
            ),
        },
    ),
)

available_functions: Type[types.Tool] = types.Tool(
    function_declarations=[
        schema_get_file_content,
        schema_get_files_info,
        schema_run_python_file,
        schema_write_file,
    ]
)

load_dotenv()
api_key: [str | None] = os.environ.get("GEMINI_API_KEY")
client: Type[genai.Client] = genai.Client(api_key=api_key)

user_prompt: str = None
is_verbose: bool = False

if (len(sys.argv) < 2) or (sys.argv[-1] == "--verbose" and len(sys.argv) < 3):
    print("input prompt not provided")
    sys.exit(1)
elif sys.argv[-1] == "--verbose":
    is_verbose = True
    user_prompt = str(sys.argv[1:-1])
else:
    user_prompt = str(sys.argv[1:])

if user_prompt is None:
    print("something went wrong, check your stupid code")
    sys.exit(1)

messages: Type[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

for _ in range(20):
    print("\n---Response---\n")
    response: Type[types.GenerateContentResponse] = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    if is_verbose:
        print(f"""\
    User prompt: {user_prompt}
    Prompt tokens: {response.usage_metadata.prompt_token_count}
    Response tokens: {response.usage_metadata.candidates_token_count}\
            """)

    if response.candidates is not None:
        for candidate in response.candidates:
            messages.append(candidate.content)

    if response.function_calls is not None:
        for function_call_part in response.function_calls:
            if (
                function_call_part.name is not None
                and len(function_call_part.args) != 0
            ):
                function_call_result: types.Content = call_function(
                    function_call_part, is_verbose
                )
                function_call_response: dict[str, Any] | None = (
                    function_call_result.parts[0].function_response.response
                )
                if (
                    function_call_response is not None
                    and isinstance(function_call_response, dict)
                    and "result" in function_call_response.keys()
                ):
                    # successful function call happened here
                    messages.append(function_call_result)
                else:
                    raise Exception(
                        "something went really really really wrong"
                    )  # supposed to be fatal hence the message ^^^
                if is_verbose:
                    print(f"-> {function_call_response}")
    else:
        print("\n\n", response.text)
        break
