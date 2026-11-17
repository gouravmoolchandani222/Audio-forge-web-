AUDIOFORGE — Full Website Starter

This project has a full-width responsive website (not a fixed-size image). Its desktop layout follows the metallic black / silver / white design. The page adapts to mobile widths.

Run locally:
1. Install Python 3.10 or newer.
2. Install FFmpeg and make sure `ffmpeg` is available in PATH.
3. Open a terminal in this folder.
4. Run: pip install -r requirements.txt
5. Run: uvicorn app:app --host 127.0.0.1 --port 8000
6. Open http://127.0.0.1:8000

AI vocal separation:
- The backend uses the open-source Demucs `htdemucs` model.
- The first separation may download model weights and can take several minutes.
- A capable CPU/GPU and sufficient RAM/disk space are recommended.
- Output files are stored in the outputs folder. Add cleanup/retention limits before public production deployment.

Already included:
- Audio upload and preview
- WAV conversion in the browser
- Trim and WAV download
- AI vocal / instrumental separation endpoint and download links

Before publishing publicly:
- Deploy to a Python host with enough memory/CPU/GPU and persistent storage.
- Add upload size limits, authentication/rate limits, automatic output cleanup, HTTPS, and privacy/retention policy.
- A public domain and search indexing are not included; this ZIP is source code, not a live website.
