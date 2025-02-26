from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import asyncio

def load_file_content(filename):
    try:
        with open(filename, "rt") as f:
            return {
                "result": f.read()
            }
    
    except Exception as e:
        return {
            "error": "Could not load file content",
        }
    
load_file_content_schema = {
    "name": "load_file_content",
    "description": "Load the content of a file",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "The name of the file",
            },
        },
        "required": ["filename"],
    },
    "output": {
        "type": "string",
        "description": "The text content of the file",
    },
}

FUNCTIONS = {"load_file_content": load_file_content}

async def handle_tool_call(session, tool_call):
    for fc in tool_call.function_calls:
        f = FUNCTIONS.get(fc.name)
        tool_response = types.LiveClientToolResponse(
            function_responses=[
                types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    response=f(**fc.args),
                )
            ]
        )
    
    await session.send(input=tool_response, end_of_turn=True)

load_dotenv()

async def main():
    model_id = "gemini-2.0-flash-exp"
    config = { 
        "tools": [{"function_declarations": [load_file_content_schema]}],
        "response_modalities": ["TEXT"]
        }

    

    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={"api_version": "v1alpha"},
    )

    async with client.aio.live.connect(model=model_id, config=config) as session:
        while True:
            message = input("> ")
            print()

            if message == "exit":
                print("Exiting...")
                break

            await session.send(input=message, end_of_turn=True)

            async for response in session.receive():
                if response.tool_call is not None:
                    await handle_tool_call(session, response.tool_call)

                elif response.server_content.model_turn is not None:
                    for part in response.server_content.model_turn.parts:
                        if part.text is not None:
                            print(part.text, end="", flush=True)

            print()


asyncio.run(main())