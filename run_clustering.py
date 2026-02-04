from app.services.topic_clustering import run_topic_clustering
from app.services.cluster_labeler import label_clusters

def main():
    print("Running topic clustering...")
    run_topic_clustering()

    print("Labeling clusters...")
    label_clusters()

    print("Done.")

if __name__ == "__main__":
    main()
