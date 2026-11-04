"""FastAPI entrypoint for Vercel."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="CSV Column Mapper", version="1.0.0", description="Compare CSV schemas and review one-to-one column mappings.")
app.include_router(router)
app.mount("/assets", StaticFiles(directory=ROOT / "public" / "assets"), name="assets")


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(ROOT / "public" / "index.html")
