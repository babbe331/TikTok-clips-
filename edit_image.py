#!/usr/bin/env python3
"""
Edit a photo with a natural-language instruction using Google's Gemini image
model ("Nano Banana", gemini-2.5-flash-image).

Example:
    python edit_image.py photo.jpg "Give the guy on the right defined pecs and abs"
    python edit_image.py photo.jpg "Give the guy on the right defined pecs and abs" out.png

Requires GOOGLE_API_KEY in the environment (same key the rest of this repo uses).
"""
import os
import sys
import time
import mimetypes

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "PASTE_YOUR_GOOGLE_KEY_HERE")

IMAGE_MODEL = "gemini-2.5-flash-image"


def edit_image(input_path, prompt, output_path=None):
    from google import genai
    from google.genai import types

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_edited.png"

    mime = mimetypes.guess_type(input_path)[0] or "image/jpeg"
    with open(input_path, "rb") as f:
        image_bytes = f.read()

    client = genai.Client(api_key=GOOGLE_API_KEY)

    print(f"[*] Editing {input_path} ({len(image_bytes)} bytes, {mime})")
    print(f"[*] Prompt: {prompt}")

    attempt = 0
    response = None
    while attempt < 3:
        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    prompt,
                ],
            )
            break
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print("    429 rate limit hit — waiting 60s before retry...")
                time.sleep(60)
                attempt += 1
            else:
                raise

    if response is None:
        raise RuntimeError("Failed to get a response after retries.")

    # Pull the first image part out of the response
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"[+] Saved edited image to {output_path}")
            return output_path
        if getattr(part, "text", None):
            print(f"    Model note: {part.text}")

    raise RuntimeError("No image was returned in the response.")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    prompt = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    if GOOGLE_API_KEY.startswith("PASTE_"):
        print("ERROR: Set GOOGLE_API_KEY in your environment first.")
        sys.exit(1)

    edit_image(input_path, prompt, output_path)


if __name__ == "__main__":
    main()
