from app.services.extractor import extract_text


def test_extract_text_invalid_file(tmp_path):
    fake_file = tmp_path / "fake.xyz"
    fake_file.write_text("data")

    result = extract_text(fake_file, "xyz")
    assert isinstance(result, str)