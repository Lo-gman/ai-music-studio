# AI Music Studio

A starter project for producing original, royalty-free **procedurally generated ambient music** and a matching visual video using GitHub Actions.

## Important
- This starter does **not** use a paid AI music API. It synthesizes music from code, so results are instrumental ambient soundscapes rather than human-composed songs or AI vocals.
- GitHub Actions can run on a schedule, but scheduled jobs are not guaranteed to start at an exact minute.
- The workflow creates a video artifact. YouTube auto-upload is intentionally a separate setup step because it requires YouTube API OAuth credentials.
- Public repositories expose source code. Never commit passwords, OAuth files, API keys, or tokens.

## First run
1. Push this project to your GitHub repository.
2. Open **Actions** in the repository and enable workflows if prompted.
3. Choose **Build a music video** > **Run workflow**.
4. Download the generated MP4 from the workflow run's **Artifacts** section.

## Enable daily builds
The workflow is scheduled for 09:00 UTC daily (12:00 Qatar time). You can change the cron expression in `.github/workflows/daily.yml`.

## YouTube publishing
Automatic publishing requires a Google Cloud project, YouTube Data API access, and OAuth credentials. Do not add these until the video-generation workflow works. New/unverified API projects may have upload restrictions. Add credentials only as GitHub Actions secrets after setting up OAuth; never place them in the repository.

## License
Use the generated audio/video according to your own publishing needs. Check platform policies and any applicable rights before monetizing.
