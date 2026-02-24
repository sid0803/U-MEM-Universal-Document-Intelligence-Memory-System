from app.core.decision_engine import classify_subject


def test_classify_ai():
    text = "This project uses machine learning and neural network models."
    result = classify_subject(text)
    assert result == "AI"


def test_classify_database():
    text = "The SQL database has a primary key constraint."
    result = classify_subject(text)
    assert result == "Database"


def test_classify_career():
    text = "My resume includes projects and experience."
    result = classify_subject(text)
    assert result == "Career"


def test_classify_finance():
    text = "The invoice amount includes GST and tax."
    result = classify_subject(text)
    assert result == "Finance"


def test_classify_general():
    text = "This is some random text without keywords."
    result = classify_subject(text)
    assert result == "General"