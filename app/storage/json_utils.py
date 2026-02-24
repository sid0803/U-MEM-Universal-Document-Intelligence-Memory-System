import json
from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)


def safe_load_json(path: Path, default):
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        backup = path.with_suffix(".corrupted")
        shutil.move(path, backup)
        logger.error("Corrupted JSON detected. Backed up to %s", backup)
        return default


def safe_write_json(path: Path, data):
    tmp = path.with_suffix(".tmp")

    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)
