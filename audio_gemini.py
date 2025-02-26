from google import genai
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import os
import asyncio

load_dotenv()

async def main():
    client = genai.Client(
        api_key = os.getenv("GOOGLE_API_KEY"),
        http_options={"api_version": "v1alpha"},
    )
    
    model_id = "gemini-2.0-flash-exp"
    config = {"response_modalities": ["AUDIO"]}
    
    with sd.OutputStream(samplerate=24000, channels=1, dtype="int16") as audio_stream:
        async with client.aio.live.connect(model=model_id, config=config) as session:
            while True:
                message = input("> ")
                print()

                if message == "exit":
                    print("Exiting...")
                    break

                await session.send(input=message, end_of_turn=True)

                async for response in session.receive():
                    if not response.server_content.turn_complete:
                        for part in response.server_content.model_turn.parts:
                            inline_data = part.inline_data
                            audio_data = np.frombuffer(inline_data.data, dtype="int16")
                            audio_stream.write(audio_data)

asyncio.run(main())