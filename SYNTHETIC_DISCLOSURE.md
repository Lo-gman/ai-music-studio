# Synthetic Content Disclosure — Quiet Frequencies

YouTube requires creators to disclose when content is made with AI or synthetic
tools. This document explains the nature of the Quiet Frequencies channel
content for YouTube's synthetic content policy.

## Content Type

All audio and video content on the Quiet Frequencies channel is
**procedurally generated using original code**. No AI music-generation APIs,
no third-party audio samples, no stock footage, and no AI-generated imagery
are used.

## What Is Synthetic Here?

- **Audio:** Synthesized from sine, saw, square, triangle, and noise
  oscillators using custom Python/numpy code. Chord progressions, melodies,
  bass lines, and textures are algorithmically composed.
- **Visuals:** Audio-reactive animations generated from the audio's FFT
  spectrum using custom Python/PIL code. All graphics are procedurally drawn.
- **Artwork:** Channel profile, banner, and thumbnails are procedurally
  generated with PIL. No third-party images or fonts with restricted licenses
  are used (DejaVu/Liberation fonts are open-source).

## What Is NOT Synthetic

- No human vocals or voices.
- No AI-generated music from third-party services (e.g., Suno, Udio, AIVA).
- No AI-generated images from third-party services (e.g., Midjourney, DALL-E).
- No stock footage or stock audio.

## YouTube Disclosure Setting

When uploading, mark the video as **containing altered or synthetic content**
per YouTube's Studio settings, and describe it as:

> "This video contains procedurally generated audio and visuals created with
> original code. No AI music-generation APIs or third-party samples were used."

## Commercial Rights

All assets are original and created by the channel operator. The code and all
generated output are suitable for commercial use and monetization.

## Dependencies and Licenses

| Package | License | Use |
|---------|---------|-----|
| numpy | BSD-3 | Audio synthesis |
| Pillow | HPND | Image/video frame generation |
| Flask | BSD-3 | Dashboard web app |
| FFmpeg | GPL/LGPL | Video/audio encoding (system tool) |
| google-api-python-client | Apache 2.0 | YouTube API upload (optional) |
| google-auth | Apache 2.0 | OAuth authentication (optional) |
