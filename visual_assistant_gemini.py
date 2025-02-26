from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from PIL import Image
import time
import pyautogui

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={"api_version": "v1alpha"},
)

def load_and_resize_image(image_path):
    with Image.open(image_path) as img:
        aspect_ratio = img.height / img.width
        new_height = int(img.width * aspect_ratio)
        return img.resize((img.width, new_height), Image.Resampling.LANCZOS)

def capture_screen():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f".\screenshots\screenshot_{timestamp}.jpeg"
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.convert("RGB")
    screenshot.save(filename, format="JPEG")
    return filename

def get_genai_response(prompt):
    print("Analyzing screen...")
    screen = load_and_resize_image(capture_screen())
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt, screen],
        config=types.GenerateContentConfig(
            system_instruction="Ignore the terminal window in the image when analyzing the image",
        )
    )
    return response.text

def main():
    while True:
        prompt = input("> ")
        print()
        if prompt == "exit":
            break
        answer = get_genai_response(prompt)
        print(answer)
        print()

if __name__ == "__main__":
    main()

