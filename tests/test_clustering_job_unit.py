import uuid
import pytest
from unittest.mock import patch
from app.core.clustering_job import clustering_job
from app.core.job_types import JobStatus


def test_clustering_job_success():
    job_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    with patch("app.core.clustering_job.update_job") as mock_update, \
         patch("app.core.clustering_job.run_topic_clustering") as mock_cluster:

        mock_cluster.return_value = {"clusters": []}

        result = clustering_job(job_id, user_id)

        # Ensure clustering returned result
        assert result == {"clusters": []}

        # Ensure RUNNING state was set
        mock_update.assert_any_call(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Starting topic clustering",
            progress=10
        )

        # Ensure SUCCESS state was set
        mock_update.assert_any_call(
            job_id,
            user_id=user_id,
            status=JobStatus.SUCCESS.value,
            message="Clustering completed successfully",
            progress=100
        )


def test_clustering_job_failure():
    job_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    with patch("app.core.clustering_job.update_job") as mock_update, \
         patch("app.core.clustering_job.run_topic_clustering") as mock_cluster:

        mock_cluster.side_effect = Exception("Clustering error")

        with pytest.raises(Exception):
            clustering_job(job_id, user_id)

        # Ensure FAILED state was set
        mock_update.assert_any_call(
            job_id,
            user_id=user_id,
            status=JobStatus.FAILED.value,
            message="Clustering failed",
            error="Clustering error"
        )