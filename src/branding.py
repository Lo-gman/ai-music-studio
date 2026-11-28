"""
AI Music Studio - Channel branding generator.
Creates QUIET FREQUENCIES brand assets: profile picture, channel banner,
video thumbnails, and category-specific artwork using Pillow.
All assets are original, procedurally generated (commercial-use safe).
"""

import os
from PIL import Image, ImageDraw, ImageFont

BRAND = "QUIET FREQUENCIES"
TAGLINE = "Ambient music for focus, sleep, and chill."

PALETTES = {
    "study":   ((12, 24, 42), (45, 83, 105)),      # deep blue
    "sleep":   ((14, 17, 48), (82, 70, 120)),      # indigo purple
    "chill":   ((27, 38, 48), (95, 116, 111)),     # teal grey
}

CATEGORY_STYLES = {
    "study": ["deep_focus", "lofi_instrumental", "piano_ambient", "concentration"],
    "sleep": ["deep_sleep", "soft_piano", "rain_atmosphere", "ocean_nature"],
    "chill": ["relaxing_electronic", "lofi_chill", "dreamy_ambient", "jazzy_background"],
}


def _font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _gradient(size, colors):
    """Create a vertical gradient image."""
    w, h = size
    im = Image.new("RGB", (w, h))
    px = im.load()
    c1, c2 = colors
    for y in range(h):
        q = y / h
        row = tuple(int(c1[k] * (1 - q) + c2[k] * q) for k in range(3))
        for x in range(w):
            px[x, y] = row
    return im


def _draw_circles(draw, w, h, accent):
    """Subtle decorative circles for a calm aesthetic."""
    for i in range(6):
        cx = w * (0.15 + i * 0.14)
        cy = h * (0.2 + (i % 2) * 0.5)
        r = w * (0.06 + i * 0.02)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(*accent, 60), width=2)


def make_profile_picture(out_path):
    """1024x1024 YouTube profile picture."""
    size = (1024, 1024)
    im = _gradient(size, PALETTES["study"])
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([150, 150, 874, 874], fill=(255, 255, 255, 18),
              outline=(255, 255, 255, 120), width=6)
    f = _font(120, bold=True)
    bbox = d.textbbox((0, 0), BRAND, font=f)
    tw = bbox[2] - bbox[0]
    d.text(((1024 - tw) / 2, 420), BRAND, font=f, fill=(255, 255, 255, 235))
    f2 = _font(40)
    bbox = d.textbbox((0, 0), TAGLINE, font=f2)
    tw = bbox[2] - bbox[0]
    d.text(((1024 - tw) / 2, 600), TAGLINE, font=f2, fill=(220, 230, 240, 200))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    im.save(out_path, quality=95)
    return out_path


def make_channel_banner(out_path):
    """2560x1440 YouTube channel banner (safe area 1546x423 centered)."""
    size = (2560, 1440)
    im = _gradient(size, PALETTES["chill"])
    d = ImageDraw.Draw(im, "RGBA")
    _draw_circles(d, 2560, 1440, (255, 255, 255))
    # Safe area rectangle
    safe = (507, 508, 2053, 931)
    d.rounded_rectangle(safe, radius=40, fill=(0, 0, 0, 40))
    f = _font(140, bold=True)
    bbox = d.textbbox((0, 0), BRAND, font=f)
    tw = bbox[2] - bbox[0]
    d.text(((2560 - tw) / 2, 620), BRAND, font=f, fill=(255, 255, 255, 230))
    f2 = _font(60)
    bbox = d.textbbox((0, 0), TAGLINE, font=f2)
    tw = bbox[2] - bbox[0]
    d.text(((2560 - tw) / 2, 800), TAGLINE, font=f2, fill=(220, 230, 240, 200))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    im.save(out_path, quality=95)
    return out_path


def make_thumbnail(cover_path, out_path, title, style="study"):
    """1280x720 YouTube thumbnail from cover art + title."""
    palette = PALETTES.get(style, PALETTES["study"])
    bg = _gradient((1280, 720), palette)
    if cover_path and os.path.exists(cover_path):
        cover = Image.open(cover_path).convert("RGB").resize((700, 700))
        bg.paste(cover, ((1280 - 700) // 2, 10))
    d = ImageDraw.Draw(bg, "RGBA")
    d.rounded_rectangle([60, 560, 1220, 690], radius=30, fill=(0, 0, 0, 100))
    f = _font(64, bold=True)
    bbox = d.textbbox((0, 0), title, font=f)
    tw = bbox[2] - bbox[0]
    d.text(((1280 - tw) / 2, 575), title, font=f, fill=(255, 255, 255, 240))
    f2 = _font(32)
    d.text((100, 20), BRAND, font=f2, fill=(255, 255, 255, 220))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    bg.save(out_path, quality=92)
    return out_path


def make_category_artwork(out_dir):
    """Generate one thumbnail per subcategory style."""
    titles = {
        "deep_focus": "Deep Focus",
        "lofi_instrumental": "Lo-fi Instrumental",
        "piano_ambient": "Piano Ambient",
        "concentration": "Concentration",
        "deep_sleep": "Deep Sleep",
        "soft_piano": "Soft Piano",
        "rain_atmosphere": "Rain Atmosphere",
        "ocean_nature": "Ocean Nature",
        "relaxing_electronic": "Relaxing Electronic",
        "lofi_chill": "Lo-fi Chill",
        "dreamy_ambient": "Dreamy Ambient",
        "jazzy_background": "Jazzy Background",
    }
    style_to_cat = {
        "deep_focus": "study", "lofi_instrumental": "study", "piano_ambient": "study", "concentration": "study",
        "deep_sleep": "sleep", "soft_piano": "sleep", "rain_atmosphere": "sleep", "ocean_nature": "sleep",
        "relaxing_electronic": "chill", "lofi_chill": "chill", "dreamy_ambient": "chill", "jazzy_background": "chill",
    }
    os.makedirs(out_dir, exist_ok=True)
    for style, title in titles.items():
        cat = style_to_cat[style]
        out = os.path.join(out_dir, f"{style}.jpg")
        make_thumbnail(None, out, title, style=cat)
    return out_dir


def main():
    out = "branding"
    make_profile_picture(os.path.join(out, "profile.jpg"))
    make_channel_banner(os.path.join(out, "banner.jpg"))
    make_category_artwork(os.path.join(out, "thumbnails"))
    print("Brand assets generated in branding/")


if __name__ == "__main__":
    main()
