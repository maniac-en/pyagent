import os


def get_files_info(working_directory: str, directory: str) -> str:
    # get absolute path for working directory
    abs_path_working_directory = os.path.abspath(working_directory)

    # get absolute path for target directory
    abs_path_target_directory = os.path.abspath(
        os.path.join(abs_path_working_directory, directory)
    )

    if not os.path.isdir(abs_path_target_directory):
        return f'Error: "{directory}" is not a directory'
    elif not abs_path_target_directory.startswith(abs_path_working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    # At this point, we've a valid directory ready to be parsed
    target_list_details: list = list()
    for path in os.listdir(abs_path_target_directory):
        details: str = str()
        path_target: str = os.path.join(abs_path_target_directory, path)
        details += f"{path}: "
        details += f"file_size={os.path.getsize(path_target)} bytes, "
        details += f"is_dir={os.path.isdir(path_target)}"
        target_list_details.append(details)

    return "- " + "\n- ".join(target for target in target_list_details)
