"""Generate images for every 'draft' post in queue/*.json.

Images land in posts/<date>/<n>.jpg (Instagram's API only accepts JPEG).
Existing files are skipped, so to re-roll a slide just delete its file and run again.
Posts move draft -> review once all their slides exist.

Env: GEMINI_API_KEY (required), IMAGE_MODEL (default gemini-nano-banana-2.1),
     IMAGE_SIZE (default 2K).
"""
import base64
import io
import json
import os
import pathlib
import sys

from google import genai
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = os.environ.get("IMAGE_MODEL", "gemini-nano-banana-2.1")
SIZE = os.environ.get("IMAGE_SIZE", "2K")

styles = json.loads((ROOT / "style" / "styles.json").read_text(encoding="utf-8"))
client = genai.Client()


def build_prompt(slide):
    prompt = f"{slide['prompt']}. {styles[slide['style']]}"
    if '"' in slide["prompt"]:  # slide asks for on-image text
        prompt += f" {styles['text_rule']}"
    return prompt


def image_bytes(prompt):
    try:  # Interactions API, as documented for the Nano Banana 2.x models
        result = client.interactions.create(
            model=MODEL,
            input=prompt,
            response_format={"type": "image", "aspect_ratio": "4:5", "image_size": SIZE},
        )
        return base64.b64decode(result.output_image.data)
    except AttributeError:  # older SDK without client.interactions
        from google.genai import types
        result = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="4:5", image_size=SIZE),
            ),
        )
        for part in result.candidates[0].content.parts:
            if part.inline_data:
                return part.inline_data.data
        raise RuntimeError(f"no image returned: {result.text}")


def generate(prompt, out):
    img = Image.open(io.BytesIO(image_bytes(prompt))).convert("RGB")
    img.save(out, "JPEG", quality=92)


def main():
    made, errors = 0, []
    for qfile in sorted((ROOT / "queue").glob("*.json")):
        posts = json.loads(qfile.read_text(encoding="utf-8"))
        for post in posts:
            if post["status"] != "draft":
                continue
            folder = ROOT / "posts" / post["date"]
            folder.mkdir(parents=True, exist_ok=True)
            ok = True
            for n, slide in enumerate(post["slides"], 1):
                out = folder / f"{n}.jpg"
                if out.exists():
                    continue
                try:
                    generate(build_prompt(slide), out)
                    made += 1
                    print(f"made {out.relative_to(ROOT)}")
                except Exception as e:  # keep going; the failed slide is retried next run
                    ok = False
                    errors.append(f"{post['date']} slide {n}: {type(e).__name__}: {e}")
                    print(f"FAILED {errors[-1]}", file=sys.stderr)
                    if len(errors) >= 3 and made == 0:  # likely a setup problem; stop wasting calls
                        break
            if ok:
                post["status"] = "review"
        qfile.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{made} images generated")
    # Actions logs need a sign-in, so keep the errors in the repo where they can be read.
    log = ROOT / "logs" / "generate_errors.txt"
    log.parent.mkdir(exist_ok=True)
    log.write_text("".join(f"{e}\n" for e in errors), encoding="utf-8")


if __name__ == "__main__":
    main()
