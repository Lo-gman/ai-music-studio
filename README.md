# AI Music Studio

A production-grade, zero-dollar operating budget engine for generating original **thematic music compositions**, layered environmental soundscapes, procedural cinematic visual artwork, and animated MP4 videos using GitHub Actions.

## Key Features

1. **Layered Music Composition Engine**:
   - Multiple instruments per track (harmony, chords, pads, lead melody, basslines, and rhythm).
   - Chord progressions, musical scales, dynamic arrangement sections (intro, verse, chorus/build, bridge, outro), fade-ins/outs, and humanized velocity.
   - 100% procedurally synthesized with no external paid audio APIs.

2. **Modular Natural Sound Library**:
   - **Water & Weather**: Window rain, downpours, storms, thunder, ocean waves (sandy & rocky), calm lake water, mountain streams, waterfalls.
   - **Wind**: Tall grass, reeds, desert dunes, soft forest wind, pine needles, mountain wind, coastal wind.
   - **Forests & Landscapes**: Rustling leaves, pine forest ambience, campfire crackling & popping embers, cave drips.
   - **Wildlife & Birds**: Songbirds, sparrows, owls, crickets, cicadas, frogs, loons, seagulls.
   - **Earth & Atmosphere**: Earth rumbles, glacier ambience, snowfall, winter cabin tone.

3. **Musical Instrument Engine**:
   - **Keyboards & Pianos**: Felt piano, Rhodes, Wurlitzer, soft grand piano, reverb piano, organs, celeste, music box.
   - **Guitars & Plucked**: Jazz guitar, acoustic fingerpicking, harp, oud, bass guitar, upright double bass.
   - **Winds & Brass**: Flute, saxophones, trumpet, clarinet.
   - **Strings & Orchestral**: Violins, cellos, lush string pads, cinematic strings.
   - **Percussion & Textures**: Soft boom-bap, dusty drums, vinyl crackle, tape hiss, room ambience.
   - **Synthesizers**: Warm analog pads, ambient pads, analog bass, evolving textures, drones.

4. **10 Thematic Composition Presets**:
   - `rainy_cafe`: Felt piano, Rhodes, jazz guitar, upright bass, brushed percussion, window rain & distant thunder.
   - `forest_morning`: Acoustic guitar, flute, felt piano, warm strings, songbirds & leaves.
   - `ocean_dreams`: Ambient piano, soft synth pads, harp, slow strings, ocean waves & coastal breeze.
   - `deep_sleep`: Minimal slow ambient pads, soft drones, sparse piano, gentle rain (sleep-safe mix).
   - `mountain_stream`: Flowing water, mountain wind, flute, acoustic guitar, soft strings.
   - `desert_night`: Oud-inspired plucked strings, desert dunes wind, cello, warm pads.
   - `winter_cabin`: Snowfall, fireplace crackle, felt piano, acoustic guitar, music box.
   - `night_forest`: Crickets, owls, night wind, ambient pads, sparse piano, subtle strings.
   - `lofi_study`: Rhodes, dusty drums, bass, jazz guitar, vinyl crackle & light rain.
   - `jazz_night`: Jazz piano, hollow-body guitar, upright bass, tenor sax, brushed drums, night ambience.

5. **Audio Mixing & Spatial Design**:
   - Profile-aware mixing (`study`, `sleep`, `chill`, `cinematic_ambient`, `nature_soundscapes`).
   - Stereo panning, reverb, delay, RMS loudness normalization, and peak limiting to prevent clipping.

6. **Thematic Video Art & Animation Engine**:
   - 16:9 full-fidelity visual scenes generated to match each theme (rainy windows, sunlit forests, moonlit oceans, starry night skies, cozy winter cabins).
   - Dynamic animated elements: moving stars, falling rain, falling snow, wave undulation, firelight glow, and audio-reactive particle energy.
   - Formatted in H.264 video + AAC audio MP4 container.

7. **Track Provenance & Automated Quality Control (QC)**:
   - Searchable `library/catalog.json` tracks IDs, seeds, chords, instruments, environments, and parameters.
   - Automated QC verifies audio length, clipping, RMS levels, visual dimensions, video stream codecs, and A/V sync before completion.

---

## Usage

### Local CLI
Generate a track with default theme (`rainy_cafe`):
```bash
python music_studio.py --theme rainy_cafe --minutes 3 --out output --video --qc
```

Choose any theme:
```bash
python music_studio.py --theme ocean_dreams --minutes 5 --out output --video --qc
```

Customize instruments or environments:
```bash
python music_studio.py --theme lofi_study --instruments felt_piano,clean_jazz_guitar --environments gentle_window_rain,vinyl_crackle
```

Run test suite:
```bash
python -m unittest discover -s tests -v
```

### GitHub Actions
The repository includes an automated workflow (`.github/workflows/daily.yml`) that can run on demand (`workflow_dispatch`) or on a daily schedule to produce downloadable MP4 video artifacts.

---

## License
Original procedural synthesis and code under the repository's open license. Zero paid API dependencies.
