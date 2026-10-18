"""Demo of the stronger film look for slides with people (not used by the pipeline yet).

Reads a few <n>_clean.jpg originals and writes posts/tests/film/<key>_<n>.jpg plus a side-by-side
before/after crop, so Trung can approve the look before stamp.py uses it.
Look (after @allen_caocaocao): warm Portra-like cast, faded blacks and softened highlights,
coarse visible grain, a little halation around bright areas, soft vignette.
"""
import pathlib

from PIL import Image, ImageChops, ImageEnhance, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLES = [("2026-10-19", 1), ("2026-10-20", 3), ("2026-10-25", 2), ("2026-10-22", 1)]


def film_people(img):
    img = img.convert("RGB")
    w, h = img.size
    # halation: bright areas bloom softly, a touch warmer
    bright = img.convert("L").point(lambda v: max(0, v - 170) * 3)
    glow = Image.merge("RGB", (bright, bright.point(lambda v: v * 0.7), bright.point(lambda v: v * 0.4)))
    glow = glow.filter(ImageFilter.GaussianBlur(w / 90))
    img = ImageChops.screen(img, glow.point(lambda v: v * 0.35))
    # faded film curve: lifted blacks, rolled-off highlights, warm cast
    r, g, b = img.split()
    r = r.point(lambda v: round(22 + v * 222 / 255))
    g = g.point(lambda v: round(18 + v * 220 / 255))
    b = b.point(lambda v: round(26 + v * 200 / 255))
    img = Image.merge("RGB", (r, g, b))
    img = ImageEnhance.Color(img).enhance(0.86)
    img = ImageEnhance.Contrast(img).enhance(0.95)
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    # coarse grain: noise made at half size and scaled up gives bigger clumps, like 400-speed film
    noise = Image.effect_noise((w // 2, h // 2), 10).resize((w, h), Image.BILINEAR).convert("RGB")
    img = ImageChops.add(img, noise, scale=1.0, offset=-128)
    fine = Image.effect_noise((w, h), 6).convert("RGB")
    img = ImageChops.add(img, fine, scale=1.0, offset=-128)
    # soft vignette
    mask = Image.radial_gradient("L").resize((w, h)).point(lambda v: min(255, v * 1.1))
    dark = ImageEnhance.Brightness(img).enhance(0.78)
    return Image.composite(dark, img, mask)


def main():
    out = ROOT / "posts" / "tests" / "film"
    out.mkdir(parents=True, exist_ok=True)
    for key, n in SAMPLES:
        src = ROOT / "posts" / key / f"{n}_clean.jpg"
        if not src.exists():
            continue
        clean = Image.open(src).convert("RGB")
        filmed = film_people(clean)
        filmed.save(out / f"{key}_{n}.jpg", "JPEG", quality=90)
        w, h = clean.size
        box = (int(w * 0.2), int(h * 0.4), int(w * 0.8), int(h * 0.4 + w * 0.6))
        pair = Image.new("RGB", (1000, 500))
        pair.paste(clean.crop(box).resize((500, 500)), (0, 0))
        pair.paste(filmed.crop(box).resize((500, 500)), (500, 0))
        pair.save(out / f"{key}_{n}_compare.jpg", "JPEG", quality=88)
        print("made", key, n)


if __name__ == "__main__":
    main()
