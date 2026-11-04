"""HTTP endpoints for CSV schema matching."""
from __future__ import annotations

import csv
import io

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.csv_reader import read_schema
from app.core.matching import match_columns, validate_mappings
from app.schemas import ReviewRequest, ReviewResponse

router = APIRouter(prefix="/api")


@router.post("/match")
async def match_csv_files(
    source_file: UploadFile = File(...),
    destination_file: UploadFile = File(...),
    cutoff: float = Form(0.80, ge=0.50, le=1.00),
) -> dict[str, object]:
    for upload in (source_file, destination_file):
        if upload.filename and not upload.filename.lower().endswith(".csv"):
            raise HTTPException(415, "Both files must have a .csv extension.")
    source = await read_schema(source_file)
    destination = await read_schema(destination_file)
    result = match_columns(source.columns, destination.columns, cutoff)
    return {
        "source": {
            "filename": source.filename,
            "columns": list(source.columns),
            "sample": list(source.row_sample),
        },
        "destination": {
            "filename": destination.filename,
            "columns": list(destination.columns),
            "sample": list(destination.row_sample),
        },
        **result,
    }


@router.post("/review", response_model=ReviewResponse)
async def review_mappings(payload: ReviewRequest) -> ReviewResponse:
    if (
        len(set(payload.source_columns)) != len(payload.source_columns)
        or len(set(payload.destination_columns)) != len(payload.destination_columns)
    ):
        raise HTTPException(422, "Column lists must not contain duplicates.")
    try:
        mappings = validate_mappings(tuple(payload.source_columns), tuple(payload.destination_columns), payload.mappings)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return ReviewResponse(mappings=mappings, count=len(mappings))


@router.post("/export")
async def export_mappings(payload: ReviewRequest) -> StreamingResponse:
    try:
        mappings = validate_mappings(tuple(payload.source_columns), tuple(payload.destination_columns), payload.mappings)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["source_column", "destination_column", "mapping_type"])
    for source in payload.source_columns:
        destination = mappings.get(source)
        if destination:
            writer.writerow([source, destination, "reviewed"])
        elif source in payload.destination_columns:
            writer.writerow([source, source, "exact"])
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="column-mappings.csv"'},
    )


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
