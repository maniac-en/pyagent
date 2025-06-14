import os
import subprocess
from typing import Type


def run_python_file(working_directory, file_path: str) -> str:
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
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    elif not os.path.exists(abs_path_target_file):
        return f'Error: File "{file_path}" not found.'
    elif not os.path.splitext(abs_path_target_file)[-1] == ".py":
        return f'Error: "{file_path}" is not a Python file.'

    try:
        py_process: Type[subprocess.CompletedProcess] = subprocess.run(
            args=["python3", abs_path_target_file], capture_output=True, timeout=30
        )

        overall_output: str = str()

        if py_process.stderr is None and py_process.stdout is None:
            overall_output += "No output produced\n"
        else:
            if py_process.stdout is not None:
                overall_output += f"STDOUT: {py_process.stdout.decode()}\n"
            if py_process.stderr is not None:
                overall_output += f"STDERR: {py_process.stderr.decode()}\n"
        if py_process.returncode != 0:
            overall_output += f"Process exited with code {py_process.returncode}\n"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    return overall_output
