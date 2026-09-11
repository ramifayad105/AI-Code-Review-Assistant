"""Tests for AIReviewer response parsing."""

from app.services.ai_reviewer import AIReviewer


def make_reviewer() -> AIReviewer:
    return AIReviewer()


def test_parse_valid_response_with_findings():
    reviewer = make_reviewer()
    raw = (
        '{"summary": "Some issues found.", "findings": ['
        '{"file_path": "a.py", "line_number": 3, "severity": "high", '
        '"category": "security", "title": "SQLi", "description": "bad", '
        '"suggestion": "use params"}]}'
    )
    result = reviewer._parse_response(raw)
    assert result["summary"] == "Some issues found."
    assert len(result["findings"]) == 1
    assert result["findings"][0]["file_path"] == "a.py"


def test_parse_fills_missing_summary_and_findings():
    reviewer = make_reviewer()
    # Valid JSON but missing both expected keys
    result = reviewer._parse_response("{}")
    assert "summary" in result
    assert result["findings"] == []


def test_parse_missing_findings_only():
    reviewer = make_reviewer()
    result = reviewer._parse_response('{"summary": "All good"}')
    assert result["summary"] == "All good"
    assert result["findings"] == []


def test_parse_invalid_json_returns_safe_fallback():
    reviewer = make_reviewer()
    result = reviewer._parse_response("not json at all")
    assert result["findings"] == []
    assert "non-JSON" in result["summary"]


def test_parse_empty_string_returns_safe_fallback():
    reviewer = make_reviewer()
    result = reviewer._parse_response("")
    assert result["findings"] == []
