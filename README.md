# CSV Column Mapper

A browser-based tool for comparing CSV schemas, reviewing suggested one-to-one column matches, and exporting confirmed mappings.

## Features
- Exact column-name matches.
- Similarity suggestions with confidence scores and ambiguity flags.
- One-to-one automatic suggestion assignment.
- Manual mapping with destination conflict validation.
- Mapping export to CSV.
- UTF-8 CSV header inspection, duplicate-header checks, and limited row samples.
- Stateless FastAPI API and responsive browser UI.

## Architecture
- **FastAPI** handles uploads, schema validation, matching, review validation, and export.
- **Pure Python matching engine** is independent of the HTTP layer.
- **Static frontend** holds reviewed mappings in browser memory; uploaded CSV bytes are never persisted.

## Limits
Each upload is limited to 4 MiB and 500 columns. The app reads headers and at most five sample rows per file. This tool maps column names only; it does not merge or transform CSV row data. Vercel's 4.5 MB request-body limit makes a 4 MiB per-file limit too large for two-file multipart requests; use smaller files where multipart overhead pushes the payload beyond that platform limit.

## Local development
```bash
uv sync --all-groups
uv run uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000.

## Checks
```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy app
```

## Deployment
The FastAPI entrypoint is `app/main.py`. Connect the repository to Vercel; Vercel detects the FastAPI app as a Python Function. Add `mapper.tejasdixit.in` to the project and configure the exact DNS target Vercel supplies.

## Privacy
Uploads are read in memory for the current request. No persistent upload storage or database is configured. Use synthetic or non-sensitive CSV data for the public demo.
