from app.core.job_store import update_job
from app.core.job_types import JobStatus
from app.services.topic_clustering import run_topic_clustering


def clustering_job(
    job_id: str,
    user_id: str,
    min_cluster_size: int = 5,
    min_samples: int = 3
):
    try:
        # Step 1 — Mark job running
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.RUNNING,
            message="Starting topic clustering",
            progress=10
        )

        # Step 2 — Execute clustering
        clusters = run_topic_clustering(
            user_id=user_id,
            min_cluster_size=min_cluster_size,
            min_samples=min_samples
        )

        # Step 3 — Mark success
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.SUCCESS.value,
            message="Clustering completed successfully",
            progress=100
        )

        return clusters

    except Exception as e:
        update_job(
            job_id,
            user_id=user_id,
            status=JobStatus.FAILED.value,
            message="Clustering failed",
            error=str(e)
        )
        raise
