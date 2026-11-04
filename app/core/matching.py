from __future__ import annotations

import difflib


def _similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, left.casefold(), right.casefold(), autojunk=False).ratio()


def match_columns(
    source_columns: tuple[str, ...],
    destination_columns: tuple[str, ...],
    cutoff: float = 0.80,
) -> dict[str, object]:
    if not 0.50 <= cutoff <= 1.0:
        raise ValueError("cutoff must be between 0.50 and 1.00")

    source_set, destination_set = set(source_columns), set(destination_columns)
    exact = sorted(source_set & destination_set)
    source_only = sorted(source_set - destination_set)
    destination_only = sorted(destination_set - source_set)

    candidates: list[tuple[float, str, str]] = []
    alternatives: dict[str, list[tuple[float, str]]] = {name: [] for name in source_only}
    for source in source_only:
        for destination in destination_only:
            score = _similarity(source, destination)
            if score >= cutoff:
                candidates.append((score, source, destination))
                alternatives[source].append((score, destination))

    candidates.sort(key=lambda item: (-item[0], item[1].casefold(), item[2].casefold()))
    assigned_sources: set[str] = set()
    assigned_destinations: set[str] = set()
    suggestions: list[dict[str, object]] = []
    for score, source, destination in candidates:
        if source in assigned_sources or destination in assigned_destinations:
            continue
        possible = sorted(alternatives[source], reverse=True)
        ambiguous = len(possible) > 1 and possible[0][0] - possible[1][0] < 0.05
        suggestions.append(
            {
                "source": source,
                "destination": destination,
                "score": round(score, 4),
                "ambiguous": ambiguous,
            }
        )
        assigned_sources.add(source)
        assigned_destinations.add(destination)

    unmatched_source = sorted(set(source_only) - assigned_sources)
    unmatched_destination = sorted(set(destination_only) - assigned_destinations)
    return {
        "exact_matches": exact,
        "source_only": source_only,
        "destination_only": destination_only,
        "suggestions": suggestions,
        "unmatched_source": unmatched_source,
        "unmatched_destination": unmatched_destination,
        "summary": {
            "source_columns": len(source_columns),
            "destination_columns": len(destination_columns),
            "exact_matches": len(exact),
            "suggestions": len(suggestions),
            "unmatched_source": len(unmatched_source),
            "unmatched_destination": len(unmatched_destination),
        },
    }


def validate_mappings(
    source_columns: tuple[str, ...],
    destination_columns: tuple[str, ...],
    mappings: dict[str, str],
) -> dict[str, str]:
    source_set, destination_set = set(source_columns), set(destination_columns)
    normalized: dict[str, str] = {}
    used_destinations: set[str] = set()
    for source, destination in mappings.items():
        if source not in source_set:
            raise ValueError(f"Unknown source column: {source}")
        if destination not in destination_set:
            raise ValueError(f"Unknown destination column: {destination}")
        if source == destination and source in destination_set:
            raise ValueError(f"{source} is already an exact match; do not remap it.")
        if destination in used_destinations:
            raise ValueError(f"Destination column already mapped: {destination}")
        normalized[source] = destination
        used_destinations.add(destination)
    return normalized
