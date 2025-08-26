import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
from functions.get_files_info import available_functions
from functions.get_files_info import get_files_info, get_file_content, write_file, run_python_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

if len(sys.argv) >= 2:
    user_prompt = sys.argv[1]
else:
    user_prompt = None

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]


system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

function_dict = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file
}

def generateModel():
    return client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )

    
def call_function(function, verbose=False):
    if verbose:
        print(f"Calling function: {function[0].name}({function[0].args})")
    else:
        print(f" - Calling function: {function[0].name}")
    if function[0].name in function_dict:
        args_to_pass = function[0].args.copy()
        args_to_pass["working_directory"] = "./calculator"
        if function[0].name == "run_python_file" or function[0].name == "get_file_content" or function[0].name == "write_file":
            args_to_pass["file_path"] = args_to_pass.pop("directory")
        result = function_dict[function[0].name](**args_to_pass)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function[0].name,
                    response={"result": result},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function[0].name,
                    response={"error": f"Unknown function: {function[0].name}"},
                )
            ],
        )
    

def main():
    if len(sys.argv) < 2:
        raise Exception("Please enter a valid command line input")
    for i in range(20):
        model = generateModel()
        
        candidates  = model.candidates or []
        for canidate in candidates :
            if canidate.content:               
                messages.append(canidate.content)
                
        function = model.function_calls or []
        verbose = "--verbose" in sys.argv
        
        if len(function) > 0:
            try:
                response = call_function(function, verbose)
                messages.append(types.Content(role="user", parts=[types.Part.from_function_response(name=function[0].name ,response=response.parts[0].function_response.response)]))
                if verbose:
                    print(f"-> {response.parts[0].function_response.response}")
            except Exception as e:
                raise Exception("Error getting response from function call") from e
        else:
            if model.text:
                print(model.text)
                break
            else:
                continue   
        if verbose:  
            print(f"User prompt: {user_prompt}")
            print(f"Prompt tokens: {model.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {model.usage_metadata.candidates_token_count}")
        


if __name__ == "__main__":
    main()
