# AI Music Studio — Quiet Frequencies

A zero-budget, fully automated YouTube music studio built for **thematic music composition, cinematic video generation, and monetization eligibility**.

Generates original instrumental ambient music, layered environmental soundscapes, audio-reactive videos, and channel branding — all with original code, no paid APIs, and no third-party audio or visual assets.

---

## Channels & Thematic Presets

| Channel | Thematic Styles & Presets | Soundscape & Instruments |
|---------|---------------------------|--------------------------|
| **Study** | `deep_focus`, `lofi_instrumental`, `piano_ambient`, `concentration`, `lofi_study` | Felt piano, Rhodes, jazz guitar, soft strings, vinyl crackle, gentle rain |
| **Sleep** | `deep_sleep`, `soft_piano`, `rain_atmosphere`, `ocean_nature`, `night_forest` | Deep sleep pads, minimal piano, crickets, night wind, ocean waves, sleep-safe mix |
| **Chill** | `relaxing_electronic`, `lofi_chill`, `dreamy_ambient`, `jazzy_background`, `rainy_cafe`, `forest_morning`, `mountain_stream`, `desert_night`, `winter_cabin`, `jazz_night` | Acoustic guitar, flutes, oud, cello, brushed percussion, flowing water, crackling fire |

---

## Monetization Readiness

| Requirement | Status |
|-------------|--------|
| Original musical compositions | Chord progressions, melody, basslines, layered arrangements |
| Coherent variety (no mass spam) | Controlled procedural seeds, harmonic scales, dynamic sections |
| Original visuals | 16:9 full HD audio-reactive procedural visual scenes matching music themes |
| Synthetic content disclosure | `SYNTHETIC_DISCLOSURE.md` + automated per-video YouTube metadata disclosure |
| Commercial-use rights | 100% original synthesis from scratch; zero third-party samples |
| Provenance records | Searchable JSON manifests (`catalog.json` / provenance records) per track |
| Zero-dollar operating budget | `numpy`, `Pillow`, `FFmpeg`, `Flask` only — no paid APIs |

---

## Project Structure

```
ai-music-studio/
├── .github/workflows/
│   ├── main.yml             # Primary GitHub Actions automated pipeline
│   └── daily.yml            # Daily scheduled and dispatch workflow
├── branding/                # Profile, banner, and category thumbnails
├── output/                  # Generated music, covers, videos, and metadata
├── src/                     # Core studio modules
│   ├── synth_engine.py      # Oscillators, envelopes, filters, reverb, delay
│   ├── music_studio.py      # Music synthesis & arrangement engine
│   ├── visualizer.py        # Audio-reactive FFT visualizer & video renderer
│   ├── video_studio.py      # Video production & YouTube metadata generator
│   ├── branding.py          # Channel artwork generator
│   ├── youtube_upload.py    # YouTube Data API v3 OAuth upload
│   └── dashboard.py         # Local production dashboard (Flask)
├── studio/                  # Extended thematic composition & natural sound engine
│   ├── theory.py            # Music theory, scales, progressions, melodies
│   ├── instruments.py       # 60+ instrument procedural synthesis
│   ├── environments.py      # 50+ natural soundscapes (water, wind, birds, earth)
│   ├── mixing.py            # Spatial mixing, AGC, limiter, EQ
│   ├── themes.py            # Thematic presets & intelligent sound selection
│   ├── visuals.py           # Thematic cinematic scene generator
│   ├── video.py             # Video MP4 pipeline
│   ├── provenance.py        # Provenance catalog & uniqueness tracking
│   └── qc.py                # Automated quality control checks
├── tests/                   # Automated unit & integration tests
├── SYNTHETIC_DISCLOSURE.md  # YouTube synthetic content disclosure
├── requirements.txt         # Free/open-source Python dependencies
├── README.md
└── LICENSE                  # MIT
```

---

## Local Installation

```bash
git clone https://github.com/Lo-gman/ai-music-studio.git
cd ai-music-studio
python -m pip install -r requirements.txt
```

---

## Running the Engine

### Option A: Thematic Studio Engine
```bash
# Generate music, cover art, animated MP4 video, and run automated QC:
python music_studio.py --theme rainy_cafe --minutes 5 --out output --video --qc
```

### Option B: Channel Arrangement Engine
```bash
# Generate track:
python src/music_studio.py --style deep_focus --minutes 5 --out output/my_track

# Render audio-reactive video:
python src/video_studio.py --audio output/my_track/music.wav --cover output/my_track/cover.jpg \
  --out output/my_track/video.mp4 --style deep_focus --title "Deep Focus - Study" --short 60
```

### Local Dashboard
```bash
python src/dashboard.py
# Open http://localhost:5000 in your browser
```

---

## Automated GitHub Actions Workflows

The workflows in `.github/workflows/main.yml` and `.github/workflows/daily.yml` automate:
1. Environment setup and dependency installation (Python 3.11 + FFmpeg).
2. Automated test suite execution (`unittest`).
3. Procedural music synthesis with selected or daily rotating theme/style.
4. Audio-reactive 16:9 full HD video rendering.
5. Automated quality control (QC) checks on audio clipping, volume levels, and A/V sync.
6. Generation of YouTube-ready title, tags, and description with synthetic content disclosure.
7. Optional automated upload to YouTube via OAuth (if secrets are configured, defaulting to `private`).
8. Packaging and storing video, audio, artwork, and provenance records as downloadable artifacts.

---

## YouTube Publishing

Set up Google Cloud OAuth per instructions in `YOUTUBE_SETUP.md`. Add credentials exclusively as GitHub Secrets:
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

All uploads default to `private` mode for safety until approved.

---

## License

MIT — All generated audio, video, and artwork is original and commercially usable.
