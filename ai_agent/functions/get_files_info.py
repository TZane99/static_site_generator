import os
import subprocess
from config import FILE_CHAR_LIMIT
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
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

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Gets the content of a file with a limit of 10,000 characters in a specified directory, constrained to working directory and for existing files.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to find the files in, relative to the working directory. If not provided, do not proceed with an unknown file location.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Overrites or creates a file within the specified directory, constraied to working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The requested text to be written in the file by the user"
            )
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs only a python file .py, constraied to working directory, existing files only, and only if the specified file is a python file.",
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

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file     
    ]
)

def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'
    else:
        try:  
            directories = os.listdir(full_path)
            file_list = []
            for dir in directories:
                file_list.append(f'- {dir}: file_size={os.path.getsize(os.path.join(full_path, dir))} bytes, is_dir={os.path.isdir(os.path.join(full_path, dir))}')
        except OSError as e:
            return f'Error: {e}'
        
    return '\n'.join(file_list)
    
def get_file_content(working_directory, file_path):
    full_file_path = os.path.join(working_directory, file_path)
    if not os.path.abspath(full_file_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{full_file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(full_file_path):
        return f'Error: File not found or is not a regular file: "{full_file_path}"'
    try:
        with open(full_file_path, "r") as f:
            if os.path.getsize(full_file_path) > 10000:
                file_content_string = f.read(FILE_CHAR_LIMIT) + f' [...File "{full_file_path}" truncated at 10000 characters]'
            else:
                file_content_string = f.read(FILE_CHAR_LIMIT)
    except (OSError, FileNotFoundError) as e:
        return f'Error: {e}'
    return file_content_string

def write_file(working_directory, file_path, content):
    full_file_path = os.path.join(working_directory, file_path)
    if not os.path.abspath(full_file_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot write to "{full_file_path}" as it is outside the permitted working directory'
    try:
        with open(full_file_path, "w") as f:
            f.write(content)
    except FileNotFoundError as e:
        return f'Error: {e}'
    
    return f'Successfully wrote to "{full_file_path}" ({len(content)} characters written)'

def run_python_file(working_directory, file_path, args=[]):
    full_file_path = os.path.join(working_directory, file_path)
    if not os.path.abspath(full_file_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(full_file_path):
        return f'Error: File "{file_path}" not found.'
    if not full_file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    command_list = ["python", full_file_path]
    command_list.extend(args)
    try:
        completed_process = subprocess.run(command_list, timeout=30, capture_output=True)
        stdout = completed_process.stdout.decode('utf-8').strip()
        stderr = completed_process.stderr.decode('utf-8').strip()
        result_message = f'STDOUT: {stdout}\nSTDERR: {stderr}\n'
        
        if completed_process.returncode != 0:
            result_message += f' Process exited with code {completed_process.returncode}'
        if not stdout and not stderr and completed_process.returncode == 0:
            return "No output produced."
        else:
            return result_message
    except Exception as e:
        return f"Error: executing Python file: {e}"