# AI Music Studio — Quiet Frequencies

A zero-budget, fully automated YouTube music studio built for **monetization
eligibility**. Generates original instrumental ambient music, audio-reactive
videos, and channel branding — all with original code, no paid APIs, and no
third-party audio or visual assets.

## Channels
- **Study** — deep focus, lo-fi instrumental, piano ambient, concentration
- **Sleep** — deep sleep ambient, soft piano, rain atmosphere, ocean/nature
- **Chill** — relaxing electronic, lo-fi chill, dreamy ambient, jazzy background

## Monetization Readiness

| Requirement | Status |
|-------------|--------|
| Original musical compositions | ✅ Chord progressions, melody, bass, arrangements |
| No repetitive mass-produced content | ✅ Every track has unique seed, progression, and arrangement |
| Original visuals | ✅ Audio-reactive FFT visualizers per category |
| Synthetic content disclosure | ✅ SYNTHETIC_DISCLOSURE.md + per-video disclosure text |
| Commercial-use rights | ✅ All assets original; no third-party samples |
| Provenance records | ✅ JSON manifest per track (seed, instruments, progression, effects) |
| No paid services | ✅ numpy, Pillow, FFmpeg, Flask only |

## Project Structure
```
ai-music-studio/
├── src/
│   ├── synth_engine.py      # Oscillators, envelopes, filters, reverb, delay
│   ├── music_studio.py      # Original arrangements + provenance records
│   ├── visualizer.py        # Audio-reactive FFT visualizer
│   ├── video_studio.py      # MP4 rendering + YouTube metadata
│   ├── branding.py          # Channel artwork generator
│   ├── youtube_upload.py    # YouTube Data API v3 OAuth upload
│   └── dashboard.py         # Flask production dashboard
├── branding/                # Profile, banner, category thumbnails
├── output/                  # Generated tracks, videos, provenance
├── .github/workflows/
│   └── daily.yml            # GitHub Actions automation
├── SYNTHETIC_DISCLOSURE.md  # YouTube synthetic content disclosure
├── requirements.txt         # Python dependencies (all free/OSI)
├── README.md                # This file
└── LICENSE                  # MIT
```

## Local Installation
```bash
git clone https://github.com/Lo-gman/ai-music-studio.git
cd ai-music-studio
py -m pip install -r requirements.txt
```

## Generate Music
```bash
py src/music_studio.py --style deep_focus --minutes 5 --out output/my_track
```
Outputs: `music.wav`, `music.mp3`, `cover.jpg`, `metadata.txt`,
`<style>_provenance.json` (full generation record).

Available styles: `deep_focus`, `lofi_instrumental`, `piano_ambient`,
`concentration`, `deep_sleep`, `soft_piano`, `rain_atmosphere`,
`ocean_nature`, `relaxing_electronic`, `lofi_chill`, `dreamy_ambient`,
`jazzy_background`.

## Render Video
```bash
py src/video_studio.py --audio output/music.wav --cover output/cover.jpg \
  --out output/video.mp4 --style deep_focus --title "Deep Focus - Study" \
  --short 60
```
`--short 60` renders a 60-second test. Omit `--short` for full-length.

## Dashboard
```bash
py src/dashboard.py
# Visit http://localhost:5000
```

## GitHub Actions
The workflow runs daily at 09:00 UTC and supports manual dispatch with style,
duration, and optional YouTube upload. Download outputs from Artifacts.

## YouTube Publishing (requires your action)
See `YOUTUBE_SETUP.md` for Google Cloud OAuth setup. Credits go in GitHub
Secrets only — never in source code. All uploads default to `private`.
No public upload without your explicit authorization.

## Synthetic Content Disclosure
See `SYNTHETIC_DISCLOSURE.md` for YouTube's synthetic content policy
compliance. Every video's description includes the disclosure statement.

## Limitations
This is procedural synthesis, not a trained AI music model. It does not
generate human vocals or lyrics. Results are original instrumental ambient
soundscapes. GitHub Actions runners have time/storage limits — very long
videos (1-8 hours) may need to be split or produced locally.

## License
MIT — all generated audio, video, and artwork is original and commercially
usable.
