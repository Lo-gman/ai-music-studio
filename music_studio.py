import math, os, random, wave, struct, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SR = 22050

def make_audio(path, minutes=5, style="study", seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    n = int(SR * 60 * minutes)
    t = np.arange(n, dtype=np.float32) / SR
    # Gentle evolving chord pad; distinct frequency sets for each mood.
    scales = {
        "study": [110.00, 130.81, 164.81, 196.00],
        "sleep": [82.41, 98.00, 123.47, 146.83],
        "chill": [98.00, 123.47, 146.83, 185.00],
    }
    freqs = scales.get(style, scales["study"])
    audio = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        wobble = 0.12 * np.sin(2 * np.pi * (0.025 + i*0.004) * t)
        phase = 2*np.pi*f*t + wobble
        slow = 0.18 + 0.07*np.sin(2*np.pi*(0.018+i*0.003)*t + i)
        audio += slow * np.sin(phase)
        audio += (slow*0.22) * np.sin(2*phase)
    # Soft filtered-noise texture, kept low in the mix.
    noise = np.random.normal(0, 1, n).astype(np.float32)
    kernel = np.ones(500, dtype=np.float32) / 500
    texture = np.convolve(noise[::100], np.ones(5, dtype=np.float32)/5, mode="same")
    texture = np.repeat(texture, 100)[:n]
    audio += 0.012 * texture
    # Gentle fade-in/out.
    fade = min(SR*8, n//4)
    env = np.ones(n, dtype=np.float32)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    audio *= env
    peak = max(0.001, float(np.max(np.abs(audio))))
    audio = np.clip(audio / peak * 0.72, -1, 1)
    pcm = (audio * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

def make_cover(path, style, title):
    palettes = {
        "study": ((12, 24, 42), (45, 83, 105)),
        "sleep": ((14, 17, 48), (82, 70, 120)),
        "chill": ((27, 38, 48), (95, 116, 111)),
    }
    a, b = palettes[style]
    im = Image.new("RGB", (1280, 720))
    px = im.load()
    for y in range(720):
        for x in range(1280):
            q = (x/1280 + y/720) / 2
            px[x,y] = tuple(int(a[k]*(1-q)+b[k]*q) for k in range(3))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((790, 80, 1190, 480), fill=(225, 220, 255, 24), outline=(240,240,255,90), width=3)
    d.ellipse((860, 150, 1120, 410), fill=(255,255,255,18))
    d.rounded_rectangle((80, 80, 730, 620), radius=24, fill=(0,0,0,55))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 58)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 27)
    except OSError:
        font = small = ImageFont.load_default()
    d.text((125, 205), "QUIET FREQUENCIES", font=small, fill=(220,230,240,230))
    d.text((125, 275), title, font=font, fill=(255,255,255,255))
    d.text((125, 390), "Original ambient soundscape", font=small, fill=(220,230,240,230))
    im.save(path, quality=94)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--style", choices=["study","sleep","chill"], default="study")
    p.add_argument("--minutes", type=int, default=5)
    p.add_argument("--out", default="output")
    args=p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    titles={"study":"Deep Focus","sleep":"Night Drift","chill":"Soft Horizon"}
    title=titles[args.style]
    audio=os.path.join(args.out, "music.wav")
    cover=os.path.join(args.out, "cover.jpg")
    make_audio(audio, max(1,min(args.minutes,30)), args.style)
    make_cover(cover,args.style,title)
    with open(os.path.join(args.out,"metadata.txt"),"w") as f:
        f.write(f"Title: {title} | Ambient Music for {args.style.title()}\\n")
        f.write("Description: Original instrumental ambient soundscape generated with custom code.\\n")
        f.write("#ambient #focusmusic #relaxingmusic #sleepmusic")
    print(f"Created {audio} and {cover}")

if __name__=="__main__":
    main()
