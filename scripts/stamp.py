"""Film finish + the small "21h" watermark in the middle of every not-yet-posted post image.

For each posts/<key>/<n>_916.jpg of a queued post that is not posted or retired:
- the unstamped original is kept as <n>_clean.jpg (used later for wallpaper packs);
- <n>_916.jpg (Threads) gets a film finish (grain, softer blacks, slightly muted colour; stronger
  grain when the slide shows people, so they look less like clean AI) and the stamp, and <n>.jpg
  (Instagram 4:5) is rebuilt from it.
The stamp's opacity follows the brightness under it: dark background ~9% white and no shadow,
bright background ~29% white with a faint dark outline, linear in between.
posts/<key>/stamped.json remembers which images are already stamped (by hash), so the script
is safe to run again; a re-rolled image (new hash) is treated as a new clean original.
"""
import hashlib
import json
import pathlib
import re

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = ROOT / "style" / "fonts" / "Quicksand-wght.ttf"
FEED_SIZE = (1080, 1350)
SIDE = 0.045        # stamp width as a share of the image width
DARK, BRIGHT = 0.35, 0.55            # background luminance range for the opacity ramp
WHITE_MIN, WHITE_MAX = 0.06, 0.19    # white opacity at dark / bright backgrounds
SHADOW_MAX = 0.05                    # dark outline opacity on bright backgrounds
GRAIN_PEOPLE, GRAIN_SCENE = 11, 5    # grain strength (gaussian sigma, 0-255 scale)
PEOPLE = re.compile(r"(woman|women|man|men|girl|boy|couple|person|people|rider|vendor|visitors?|tourists?|shoppers?|crowd|mother|daughter|florist|rower)", re.I)
VERSION = 3                          # bump when the look changes: every image is re-stamped from its clean original


def sha(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def ramp(lum, lo, hi):
    t = min(1.0, max(0.0, (lum - DARK) / (BRIGHT - DARK)))
    return lo + (hi - lo) * t


def stamp(img):
    img = img.convert("RGB")
    w, h = img.size
    side = round(w * SIDE)
    x0, y0 = (w - side) // 2, (h - side) // 2
    box = (x0, y0, x0 + side, y0 + side)
    lum = sum(img.crop(box).convert("L").getdata()) / (side * side * 255)
    white = round(255 * ramp(lum, WHITE_MIN, WHITE_MAX))
    shadow = round(255 * ramp(lum, 0.0, SHADOW_MAX)) if lum > (DARK + BRIGHT) / 2 else 0

    font = ImageFont.truetype(str(FONT), size=round(side * 0.40))
    try:
        font.set_variation_by_name("Bold")
    except Exception:
        pass
    lw = max(1, round(side * 0.055))
    radius = round(side * 0.18)
    centre = (x0 + side / 2, y0 + side / 2 + side * 0.01)

    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if shadow:
        d.rounded_rectangle(box, radius=radius, outline=(0, 0, 0, shadow), width=round(lw * 2.4))
        d.text(centre, "21h", font=font, anchor="mm", fill=(0, 0, 0, 0),
               stroke_width=max(1, round(lw * 0.6)), stroke_fill=(0, 0, 0, shadow))
    d.rounded_rectangle(box, radius=radius, outline=(255, 255, 255, white), width=lw)
    d.text(centre, "21h", font=font, anchor="mm", fill=(255, 255, 255, white))
    out = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return out, lum, white


def film(img, people):
    """Soft film finish: tiny blur, lifted blacks, a little less saturation, monochrome grain."""
    img = img.convert("RGB").filter(ImageFilter.GaussianBlur(0.6 if people else 0.3))
    img = img.point(lambda v: round(10 + v * 236 / 255))
    img = ImageEnhance.Color(img).enhance(0.92 if people else 0.96)
    noise = Image.effect_noise(img.size, GRAIN_PEOPLE if people else GRAIN_SCENE).convert("RGB")
    return ImageChops.add(img, noise, scale=1.0, offset=-128)


def feed_image(full, out):
    canvas = Image.new("RGB", FEED_SIZE, "black")
    fitted = full.resize((round(full.width * FEED_SIZE[1] / full.height), FEED_SIZE[1]), Image.LANCZOS)
    canvas.paste(fitted, ((FEED_SIZE[0] - fitted.width) // 2, 0))
    canvas.save(out, "JPEG", quality=93)


def main():
    posts = {}
    for qfile in (ROOT / "queue").glob("*.json"):
        for p in json.loads(qfile.read_text(encoding="utf-8")):
            if p.get("status") in ("review", "approved") and p["date"][:1].isdigit():
                posts[p["date"]] = p
    keys = set(posts)
    log = []
    for key in sorted(keys):
        folder = ROOT / "posts" / key
        if not folder.is_dir():
            continue
        marker = folder / "stamped.json"
        done = json.loads(marker.read_text(encoding="utf-8")) if marker.exists() else {}
        same_look = done.get("version", 1) == VERSION
        for full in sorted(folder.glob("*_916.jpg")):
            n = full.name.split("_")[0]
            clean = folder / f"{n}_clean.jpg"
            if done.get(n) == sha(full):
                if same_look:
                    continue  # already stamped with the current look
            else:
                Image.open(full).save(clean, "JPEG", quality=95)   # fresh, unstamped render
            slides = posts[key].get("slides", [])
            prompt = slides[int(n) - 1].get("prompt", "") if n.isdigit() and int(n) <= len(slides) else ""
            people = bool(PEOPLE.search(NO_PEOPLE.sub("", prompt)))
            stamped, lum, white = stamp(film(Image.open(clean), people))
            stamped.save(full, "JPEG", quality=92)
            feed_image(stamped, folder / f"{n}.jpg")
            done[n] = sha(full)
            log.append(f"{key} slide {n}: background {lum:.2f}, white {white / 2.55:.0f}%, film {people if people else scene}")
        done["version"] = VERSION
        marker.write_text(json.dumps(done, indent=2) + "\n", encoding="utf-8")
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / "stamp.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log) or "nothing to stamp")


if __name__ == "__main__":
    main()
