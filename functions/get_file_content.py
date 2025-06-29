import os

MAX_CHARS: int = 10000


def get_file_content(working_directory, file_path: str) -> str:
    # Check is file_path parameter is passed or not
    if file_path is None:
        return f'Error: file_path cannot be "{file_path}"'

    # get absolute path for working directory
    abs_path_working_directory = os.path.abspath(working_directory)

    # get absolute path for target file
    abs_path_target_file = os.path.abspath(
        os.path.join(abs_path_working_directory, file_path)
    )

    if not os.path.isfile(abs_path_target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    elif not abs_path_target_file.startswith(abs_path_working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    # At this point, we've a valid file ready to be parsed
    with open(abs_path_target_file, "r") as f:
        file_contents: str = f.read(MAX_CHARS)
        f.close()

    if len(file_contents) == 10000:
        file_contents += f'\n[...File "{file_path}" truncated at 10000 characters]'
    return file_contents
