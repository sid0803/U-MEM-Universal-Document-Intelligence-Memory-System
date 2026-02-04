from pathlib import Path

def detect_file_type(path: Path):
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return "pdf"
    if suffix == ".txt":
        return "txt"
    if suffix == ".docx":
        return "docx"
    if suffix in [".png", ".jpg", ".jpeg"]:
        return "image"

    return "unknown"
