import os
import sys
from typing import Type

from dotenv import load_dotenv
from google import genai
from google.genai import types


system_prompt: str = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info: Type[types.FunctionDeclaration] = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

available_functions: Type[types.Tool] = types.Tool(
    function_declarations=[
        schema_get_files_info,
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

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

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

if response.function_calls is not None:
    for function_call_part in response.function_calls:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
else:
    print(response.text)
