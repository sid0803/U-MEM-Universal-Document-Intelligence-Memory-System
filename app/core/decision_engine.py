def classify_subject(text: str) -> str:
    text = text.lower()

    SUBJECT_KEYWORDS = {
        "AI": [
            "machine learning", "deep learning", "neural network",
            "artificial intelligence", "nlp", "computer vision"
        ],
        "Database": [
            "sql", "database", "normalization",
            "primary key", "foreign key"
        ],
        "Career": [
            "resume", "experience", "skills",
            "project", "education"
        ],
        "Finance": [
            "invoice", "tax", "gst", "amount",
            "profit", "loss"
        ]
    }

    for subject, keywords in SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return subject

    return "General"
