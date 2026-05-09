from src.retriever import retrieve_context


def test_known_genre_returns_description():
    result = retrieve_context("lofi", "chill")
    assert "Low-fidelity" in result
    assert "Relaxed" in result


def test_unknown_genre_falls_back_gracefully():
    result = retrieve_context("klezmer", "happy")
    assert "not a recognised genre" in result
    assert "Uplifting" in result or "optimistic" in result or "positive" in result


def test_case_insensitive():
    upper = retrieve_context("LoFi", "CHILL")
    # Lookup resolves to the same KB entries regardless of input casing
    assert "Low-fidelity" in upper
    assert "Relaxed" in upper
