from pathlib import Path
import shutil

BASE_DIR = Path("data/subjects")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def move_file(
    file_path: Path,
    document_type: str,
    subject: str
) -> Path:
    """
    Moves file to:
    data/subjects/<DocumentType>/<Subject>/<filename>
    """
    target_dir = BASE_DIR / document_type / subject
    target_dir.mkdir(parents=True, exist_ok=True)

    final_path = target_dir / file_path.name
    shutil.move(str(file_path), str(final_path))

    return final_path
