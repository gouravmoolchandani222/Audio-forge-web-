from pathlib import Path
import shutil, subprocess, uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)
app = FastAPI(title="AudioForge API")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")

@app.post("/api/separate")
async def separate(file: UploadFile = File(...)):
    allowed = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"}
    suffix = Path(file.filename or "audio").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, "Unsupported audio format.")
    job = uuid.uuid4().hex
    source_dir = UPLOADS / job
    source_dir.mkdir(parents=True, exist_ok=True)
    source = source_dir / f"input{suffix}"
    with source.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    try:
        # Demucs separates the original track into vocals and accompaniment.
        proc = subprocess.run(
            ["python", "-m", "demucs", "--two-stems=vocals",
             "-n", "htdemucs", "-o", str(OUTPUTS / job), str(source)],
            capture_output=True, text=True, timeout=3600
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr[-2500:] or "Demucs processing failed")
        stem_dir = OUTPUTS / job / "htdemucs" / source.stem
        vocals = stem_dir / "vocals.wav"
        instrumental = stem_dir / "no_vocals.wav"
        if not vocals.exists() or not instrumental.exists():
            raise RuntimeError("AI model did not produce both audio stems.")
        return {
            "vocals_url": f"/api/download/{job}/vocals",
            "instrumental_url": f"/api/download/{job}/instrumental"
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "AI separation timed out.")
    except Exception as exc:
        raise HTTPException(500, str(exc))
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)

@app.get("/api/download/{job}/{stem}")
def download_stem(job: str, stem: str):
    if stem not in {"vocals", "instrumental"} or not job.isalnum():
        raise HTTPException(400, "Invalid download request.")
    path = OUTPUTS / job / "htdemucs"
    matches = list(path.glob(f"*/{'vocals.wav' if stem == 'vocals' else 'no_vocals.wav'}"))
    if not matches:
        raise HTTPException(404, "Audio result not found.")
    return FileResponse(matches[0], filename=f"audioforge-{stem}.wav", media_type="audio/wav")
