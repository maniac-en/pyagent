import os
import sys
from typing import Type

from dotenv import load_dotenv
from google import genai
from google.genai import types


system_prompt: str = (
    'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'
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

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(system_instruction=system_prompt),
)

print(response.text)
if is_verbose:
    print(f"""\
User prompt: {user_prompt}
Prompt tokens: {response.usage_metadata.prompt_token_count}
Response tokens: {response.usage_metadata.candidates_token_count}\
        """)
