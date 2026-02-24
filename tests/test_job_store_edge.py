import uuid
import pytest
from app.core.job_store import update_job


def test_update_nonexistent_job():
    with pytest.raises(ValueError):
        update_job(
            job_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            status="SUCCESS"
        )