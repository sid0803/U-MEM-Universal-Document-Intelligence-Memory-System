from app.services.text_normalizer import normalize_text

def test_text_normalizer_basic():
    text = "  Hello   World  "
    normalized = normalize_text(text)

    assert normalized == "hello world"