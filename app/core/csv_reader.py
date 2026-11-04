"""Safe, bounded CSV header inspection."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from fastapi import HTTPException, UploadFile

MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_COLUMNS = 500
SAMPLE_ROWS = 5


@dataclass(frozen=True)
class CSVSchema:
    filename: str
    columns: tuple[str, ...]
    row_sample: tuple[dict[str, str], ...]


async def read_schema(upload: UploadFile) -> CSVSchema:
    raw = await upload.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(413, "Each CSV must be 4 MiB or smaller.")
    if not raw:
        raise HTTPException(422, "Uploaded CSV is empty.")
    try:
        reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
        headers = next(reader, None)
    except (csv.Error, UnicodeDecodeError) as exc:
        raise HTTPException(422, "Unable to read the CSV header. Use a valid UTF-8 CSV.") from exc
    if not headers:
        raise HTTPException(422, "CSV must contain a header row.")
    if len(headers) > MAX_COLUMNS:
        raise HTTPException(422, f"CSV exceeds the {MAX_COLUMNS}-column limit.")
    if any(not header.strip() for header in headers):
        raise HTTPException(422, "CSV contains an empty column name.")
    if len(set(headers)) != len(headers):
        raise HTTPException(422, "CSV contains duplicate column names.")
    samples: list[dict[str, str]] = []
    try:
        for row in reader:
            if len(samples) >= SAMPLE_ROWS:
                break
            if len(row) == len(headers):
                samples.append(dict(zip(headers, row, strict=True)))
    except csv.Error as exc:
        raise HTTPException(422, "Unable to parse CSV rows.") from exc
    return CSVSchema(upload.filename or "uploaded.csv", tuple(headers), tuple(samples))
