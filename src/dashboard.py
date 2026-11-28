"""
AI Music Studio - Lightweight web dashboard.
Scans provenance records to show generated tracks, production status, and
downloads. Run locally: python src/dashboard.py
"""

import os
import json
import glob
from datetime import datetime
from flask import Flask, render_template_string, send_from_directory, jsonify

app = Flask(__name__)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")
HISTORY_FILE = os.path.join(ROOT, "production_history.json")


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-100:], f, indent=2)


def scan_provenance():
    """Scan output/ for provenance JSON files and build track list."""
    tracks = []
    if not os.path.exists(OUTPUT_DIR):
        return tracks
    for prov_path in glob.glob(os.path.join(OUTPUT_DIR, "*", "*_provenance.json")):
        try:
            with open(prov_path, "r", encoding="utf-8") as f:
                prov = json.load(f)
            dir_name = os.path.dirname(prov_path)
            wav = prov.get("wav", "")
            mp3 = prov.get("mp3", "")
            cover = os.path.join(dir_name, "cover.jpg")
            video = os.path.join(dir_name, "video.mp4")
            title_meta = os.path.join(dir_name, "metadata.txt")
            created = prov.get("generated_at", "")
            tracks.append({
                "style": prov.get("style", ""),
                "title": prov.get("title", ""),
                "category": prov.get("category", ""),
                "minutes": prov.get("minutes", 0),
                "seed": prov.get("seed", 0),
                "created": created,
                "wav": os.path.basename(wav) if wav else None,
                "mp3": os.path.basename(mp3) if mp3 else None,
                "cover": os.path.basename(cover) if os.path.exists(cover) else None,
                "video": os.path.basename(video) if os.path.exists(video) else None,
                "provenance": os.path.basename(prov_path),
            })
        except Exception:
            continue
    # Also merge history file entries
    history = load_history()
    for entry in history:
        if not any(t.get("style") == entry.get("style")
                   and t.get("seed") == entry.get("seed")
                   and t.get("created") == entry.get("created") for t in tracks):
            tracks.append({
                "style": entry.get("style", ""),
                "title": entry.get("title", ""),
                "category": entry.get("category", ""),
                "minutes": entry.get("minutes", 0),
                "seed": entry.get("seed", 0),
                "created": entry.get("created", ""),
                "wav": os.path.basename(entry.get("wav", "")) if entry.get("wav") else None,
                "mp3": os.path.basename(entry.get("mp3", "")) if entry.get("mp3") else None,
                "cover": os.path.basename(entry.get("cover", "")) if entry.get("cover") else None,
                "video": os.path.basename(entry.get("video", "")) if entry.get("video") else None,
            })
    tracks.sort(key=lambda t: t.get("created", ""), reverse=True)
    return tracks


HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Quiet Frequencies - Production Dashboard</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0b0e16;color:#e8eef7;margin:0;padding:24px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}
h1{font-size:1.5rem;margin:0;letter-spacing:0.12em;color:#fff}
.sub{color:#93a3b8;font-size:0.9rem}
table{width:100%;border-collapse:collapse;background:#12192b;border-radius:10px;overflow:hidden}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid #1f2a44}
th{background:#16203a;color:#93a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em}
tr:hover{background:#172238}
.tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.7rem;background:#1f2a44;color:#93a3b8}
.study{color:#7ec4f7} .sleep{color:#b8a7ff} .chill{color:#9cd6c8}
a.btn{display:inline-block;padding:6px 12px;border-radius:6px;background:#2563eb;color:#fff;text-decoration:none;font-size:0.85rem;margin-right:4px}
a.btn:hover{background:#1d4ed8}
.empty{text-align:center;color:#64748b;padding:40px}
.status{display:flex;gap:16px;margin-bottom:20px}
.card{background:#12192b;padding:16px;border-radius:10px;flex:1}
.big{font-size:1.25rem;font-weight:700;color:#fff}
.small{color:#93a3b8;font-size:0.85rem}
.prov{font-size:0.75rem;color:#64748b;margin-top:4px}
</style>
</head>
<body>
<header>
<div><h1>Quiet Frequencies</h1><div class="sub">AI Music Studio Production Dashboard</div></div>
<div class="sub">Tracks: {{tracks|length}} &bull; Last run: {{last_run}}</div>
</header>

<div class="status">
<div class="card"><div class="small">Total tracks</div><div class="big">{{tracks|length}}</div></div>
<div class="card"><div class="small">Study</div><div class="big">{{study_count}}</div></div>
<div class="card"><div class="small">Sleep</div><div class="big">{{sleep_count}}</div></div>
<div class="card"><div class="small">Chill</div><div class="big">{{chill_count}}</div></div>
</div>

{% if not tracks %}
<div class="empty">No tracks generated yet. Run a production job from GitHub Actions to generate your first track.</div>
{% else %}
<table>
<thead><tr><th>Style</th><th>Title</th><th>Category</th><th>Length</th><th>Created</th><th>Downloads</th></tr></thead>
<tbody>
{% for t in tracks %}
<tr>
<td><span class="tag {{t.category}}">{{t.category}}</span> {{t.style}}</td>
<td>{{t.title}}<div class="prov">seed {{t.seed}} &bull; {{t.minutes}} min</div></td>
<td>{{t.category|capitalize}}</td>
<td>{{t.minutes}} min</td>
<td>{{t.created}}</td>
<td>
{% if t.wav %}<a class="btn" href="/download/{{t.wav}}">WAV</a>{% endif %}
{% if t.mp3 %}<a class="btn" href="/download/{{t.mp3}}">MP3</a>{% endif %}
{% if t.video %}<a class="btn" href="/download/{{t.video}}">MP4</a>{% endif %}
{% if t.cover %}<a class="btn" href="/download/{{t.cover}}">JPG</a>{% endif %}
{% if t.provenance %}<a class="btn" href="/download/{{t.provenance}}" style="background:#6b7280">PROVENANCE</a>{% endif %}
</td>
</tr>
{% endfor %}
</tbody>
</table>
{% endif %}
</body>
</html>
"""


@app.route("/")
def index():
    tracks = scan_provenance()
    cats = {"study": 0, "sleep": 0, "chill": 0}
    for t in tracks:
        c = t["category"]
        if c in cats:
            cats[c] += 1
    last_run = tracks[0]["created"] if tracks else "Never"
    return render_template_string(
        HTML, tracks=tracks, last_run=last_run,
        study_count=cats["study"], sleep_count=cats["sleep"], chill_count=cats["chill"]
    )


@app.route("/download/<path:filename>")
def download(filename):
    for d in [OUTPUT_DIR, ROOT]:
        path = os.path.join(d, filename)
        if os.path.exists(path):
            return send_from_directory(d, filename, as_attachment=True)
    return "Not found", 404


@app.route("/api/tracks")
def api_tracks():
    return jsonify(scan_provenance())


def record_track(meta, video_path=None):
    history = load_history()
    entry = dict(meta)
    entry["created"] = datetime.now().isoformat() + "Z"
    entry["video"] = os.path.basename(video_path) if video_path else None
    history.insert(0, entry)
    save_history(history)


def main():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)


if __name__ == "__main__":
    main()
