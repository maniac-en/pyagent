import os

def write_file(working_directory, file_path, content: str) -> str:
    # Check is file_path parameter is passed or not
    if file_path is None:
        return f'Error: file_path cannot be "{file_path}"'

    # get absolute path for working directory
    abs_path_working_directory = os.path.abspath(working_directory)

    # get absolute path for target file
    abs_path_target_file = os.path.abspath(
        os.path.join(abs_path_working_directory, file_path)
    )

    if not abs_path_target_file.startswith(abs_path_working_directory):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    elif not os.path.exists(abs_path_target_file):
        os.makedirs(os.path.dirname(abs_path_target_file), exist_ok=True)
    elif not os.path.isfile(abs_path_target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(abs_path_target_file, 'w') as f:
            f.write(content)
            f.close()
    except Exception as e:
        return f'Error: {e.message}'
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
