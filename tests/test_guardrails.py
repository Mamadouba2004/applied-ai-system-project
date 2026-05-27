import pytest
from src.guardrails import validate

_LONG_TEXT = "This is a sufficiently long response that mentions the song Midnight Coding by LoRoom, which fits the user profile well because it has a chill mood and medium energy level suitable for focused listening sessions."


def test_empty_response_raises():
    with pytest.raises(ValueError, match="empty"):
        validate("", [])


def test_short_response_raises():
    with pytest.raises(ValueError, match="too short"):
        validate("OK", [])


def test_no_title_mentioned_raises():
    long_text_no_title = "This is a sufficiently long response about music in general that does not mention any specific song title from the recommended list at all."
    with pytest.raises(ValueError, match="does not mention any recommended song title"):
        validate(long_text_no_title, [{"title": "Midnight Coding", "score": 6.98}])


def test_valid_response_passes():
    result = validate(_LONG_TEXT, [{"title": "Midnight Coding", "score": 6.98}])
    assert result == _LONG_TEXT


def test_negative_score_raises():
    with pytest.raises(ValueError, match="negative score"):
        validate(_LONG_TEXT, [{"title": "X", "score": -1}])
