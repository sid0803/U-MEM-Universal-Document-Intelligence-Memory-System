from app.storage.metadata import load_clusters


def check_cluster_health():
    clusters = load_clusters()
    health_report = []

    for c in clusters:
        issues = []

        if c.get("num_documents", 0) < 2:
            issues.append("Too few documents")

        if c.get("confidence", 0) < 0.15:
            issues.append("Low confidence")

        health_report.append({
            "cluster_id": c["cluster_id"],
            "label": c.get("label"),
            "issues": issues,
            "status": "healthy" if not issues else "warning"
        })

    return health_report
