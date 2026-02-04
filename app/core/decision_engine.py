def classify_subject(text: str) -> str:
    text = text.lower()

    SUBJECT_KEYWORDS = {
        "AI": [
            "machine learning", "deep learning", "neural network",
            "artificial intelligence", "nlp", "computer vision"
        ],
        "Database": [
            "sql", "database", "normalization", "er diagram",
            "primary key", "foreign key"
        ],
        "Finance": [
            "invoice", "amount", "tax", "gst", "balance sheet",
            "profit", "loss"
        ],
        "Career": [
            "resume", "experience", "skills", "education",
            "project", "internship"
        ],
    }

    for subject, keywords in SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return subject

    return "General"
