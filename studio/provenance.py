"""Track provenance and searchable content library."""

from __future__ import annotations

import json
import os
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def load_catalog(catalog_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(catalog_path):
        return []
    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def is_unique_track(catalog: List[Dict[str, Any]], theme_id: str, seed: int) -> bool:
    return not any(item.get("theme") == theme_id and item.get("seed") == seed for item in catalog)


def record_provenance(
    catalog_path: str,
    track_id: str,
    theme_id: str,
    seed: int,
    tempo_bpm: int,
    key_name: str,
    chord_progression: List[str],
    instruments: Dict[str, str],
    environments: List[str],
    arrangement: List[str],
    duration_seconds: float,
    audio_filename: str,
    video_filename: Optional[str],
    artwork_filename: str,
    metadata_filename: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    os.makedirs(os.path.dirname(os.path.abspath(catalog_path)), exist_ok=True)
    catalog = load_catalog(catalog_path)
    entry: Dict[str, Any] = {
        "track_id": track_id,
        "theme": theme_id,
        "seed": seed,
        "tempo_bpm": tempo_bpm,
        "key": key_name,
        "chord_progression": chord_progression,
        "instruments": instruments,
        "environmental_sounds": environments,
        "arrangement": arrangement,
        "duration_seconds": round(duration_seconds, 2),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "audio_filename": audio_filename,
        "video_filename": video_filename,
        "artwork_filename": artwork_filename,
        "metadata_filename": metadata_filename,
        "parameters": parameters,
        "dependencies": {
            "python": sys.version.split()[0],
            "platform": platform.system(),
        },
    }
    catalog.append(entry)
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    return entry


def search_catalog(catalog_path: str, theme: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    catalog = load_catalog(catalog_path)
    results = []
    for item in catalog:
        if theme and item.get("theme") != theme:
            continue
        if query:
            blob = json.dumps(item).lower()
            if query.lower() not in blob:
                continue
        results.append(item)
    return results
