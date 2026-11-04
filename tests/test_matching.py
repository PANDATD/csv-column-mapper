from app.core.matching import match_columns, validate_mappings


def test_exact_matches_and_suggestions_are_reported() -> None:
    result = match_columns(
        ("id", "first_name", "email"),
        ("id", "firstName", "email_address"),
        0.70,
    )
    assert result["exact_matches"] == ["id"]
    assert result["summary"]["source_columns"] == 3


def test_destination_is_assigned_at_most_once() -> None:
    result = match_columns(("user_name", "username"), ("userName",), 0.50)
    destinations = [item["destination"] for item in result["suggestions"]]
    assert len(destinations) == len(set(destinations)) == 1


def test_duplicate_destination_is_rejected() -> None:
    try:
        validate_mappings(("a", "b"), ("x",), {"a": "x", "b": "x"})
    except ValueError as exc:
        assert "already mapped" in str(exc)
    else:
        raise AssertionError("Expected duplicate destination rejection")
