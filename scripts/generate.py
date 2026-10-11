"""Generate images for every 'draft' post in queue/*.json.

Each slide is rendered once as a 9:16 phone wallpaper (posts/<date>/<n>_916.jpg).
The feed image posts/<date>/<n>.jpg is made from it for free: the whole 9:16 picture
centred on a black 4:5 canvas (Instagram's API rejects 9:16 feed images).
A slide's optional "subtitle" is drawn by this script, never by the model, so every
subtitle uses the same font, colour and position.

Existing files are skipped, so to re-roll a slide delete both of its files and run again.
If only <n>_916.jpg exists, the feed image is rebuilt from it without calling the API.
Subtitled slides also keep a clean <n>_raw.jpg; delete <n>.jpg and <n>_916.jpg to redraw the
subtitle (new text or "subtitle_y" position) without calling the API.
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
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = os.environ.get("IMAGE_MODEL", "gemini-nano-banana-2.1")
SIZE = os.environ.get("IMAGE_SIZE", "2K")
ASPECT = "9:16"
FEED_SIZE = (1080, 1350)  # Instagram's 4:5 portrait size
SUBTITLE_FONT = ROOT / "style" / "fonts" / "NotoSerif-Italic.ttf"
SUBTITLE_COLOUR = (246, 228, 158)  # pale yellow, like film subtitles
SAFE_ZONE = "Keep the subject fully inside the frame, slightly above the bottom edge."
SUBTITLE_SPACE = ("Keep the lowest fifth of the image calm and simple, with nothing important there, "
                  "because a subtitle will be added later. Do not draw any text.")

styles = json.loads((ROOT / "style" / "styles.json").read_text(encoding="utf-8"))
client = genai.Client()


def build_prompt(slide):
    prompt = f"{slide['prompt']}. {styles[slide['style']]} {SAFE_ZONE}"
    if slide.get("subtitle"):
        prompt += f" {SUBTITLE_SPACE}"
    return prompt


def image_bytes(prompt):
    try:  # Interactions API, as documented for the Nano Banana 2.x models
        result = client.interactions.create(
            model=MODEL,
            input=prompt,
            response_format={"type": "image", "aspect_ratio": ASPECT, "image_size": SIZE},
        )
        return base64.b64decode(result.output_image.data)
    except AttributeError:  # older SDK without client.interactions
        from google.genai import types
        result = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=ASPECT, image_size=SIZE),
            ),
        )
        for part in result.candidates[0].content.parts:
            if part.inline_data:
                return part.inline_data.data
        raise RuntimeError(f"no image returned: {result.text}")


def add_subtitle(img, text, y=0.9):
    """Draw a film-style subtitle centred at y (fraction of the height) on a copy of img."""
    img = img.copy()
    w, h = img.size
    font = ImageFont.truetype(str(SUBTITLE_FONT), size=round(w * 0.042))
    try:
        font.set_variation_by_name("Italic")  # regular weight of the variable font
    except Exception:
        pass
    draw = ImageDraw.Draw(img)
    draw.text((w / 2, h * y), text, font=font, fill=SUBTITLE_COLOUR, anchor="mm",
              stroke_width=max(2, w // 600), stroke_fill=(20, 16, 10))
    return img


def feed_image(full, out):
    """Centre the whole 9:16 image on a black 4:5 canvas and save it as <n>.jpg."""
    canvas = Image.new("RGB", FEED_SIZE, "black")
    fitted = full.resize((round(full.width * FEED_SIZE[1] / full.height), FEED_SIZE[1]), Image.LANCZOS)
    canvas.paste(fitted, ((FEED_SIZE[0] - fitted.width) // 2, 0))
    canvas.save(out, "JPEG", quality=93)


def generate(slide, out):
    """Make <n>_916.jpg (one API call) and <n>.jpg. Returns True if the API was called."""
    full_path = out.with_name(f"{out.stem}_916.jpg")
    raw_path = out.with_name(f"{out.stem}_raw.jpg")  # clean copy, so subtitles can be redone for free
    called = False
    if raw_path.exists():
        img = Image.open(raw_path).convert("RGB")
    elif full_path.exists():  # older render: subtitle (if any) is already baked in
        feed_image(Image.open(full_path).convert("RGB"), out)
        return False
    else:
        img = Image.open(io.BytesIO(image_bytes(build_prompt(slide)))).convert("RGB")
        if slide.get("subtitle"):
            img.save(raw_path, "JPEG", quality=92)
        called = True
    if slide.get("subtitle"):
        img = add_subtitle(img, slide["subtitle"], slide.get("subtitle_y", 0.9))
    img.save(full_path, "JPEG", quality=92)
    feed_image(img, out)
    return called


def main():
    made, errors, stop = 0, [], False
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
                    if generate(slide, out):
                        made += 1
                    print(f"made {out.relative_to(ROOT)}")
                except Exception as e:  # keep going; the failed slide is retried next run
                    ok = False
                    errors.append(f"{post['date']} slide {n}: {type(e).__name__}: {e}")
                    print(f"FAILED {errors[-1]}", file=sys.stderr)
                    if len(errors) >= 3 and made == 0:  # likely a setup problem; stop wasting calls
                        stop = True
                        break
            if ok:
                post["status"] = "review"
            if stop:
                break
        qfile.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{made} images generated")
    # Actions logs need a sign-in, so keep the errors in the repo where they can be read.
    log = ROOT / "logs" / "generate_errors.txt"
    log.parent.mkdir(exist_ok=True)
    log.write_text("".join(f"{e}\n" for e in errors), encoding="utf-8")


if __name__ == "__main__":
    main()
