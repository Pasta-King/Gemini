from google import genai
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
async def main():
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={"api_version": "v1alpha"},
    )

    model_id = "gemini-2.0-flash-exp"
    config = {"response_modalities": ["TEXT"]}
    async with client.aio.live.connect(model=model_id, config=config) as session:
        await session.send(input="Hello", end_of_turn=True)

        async for response in session.receive():
            if not response.server_content.turn_complete:
                for part in response.server_content.model_turn.parts:
                    print(part.text, end="", flush=True)

asyncio.run(main())