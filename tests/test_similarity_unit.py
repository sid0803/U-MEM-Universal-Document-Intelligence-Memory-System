from app.services.similarity import cosine_similarity


def test_similarity_same_vector():
    vec = [1, 2, 3]
    score = cosine_similarity(vec, vec)
    assert round(score, 5) == 1.0


def test_similarity_orthogonal():
    vec1 = [1, 0]
    vec2 = [0, 1]
    score = cosine_similarity(vec1, vec2)
    assert round(score, 5) == 0.0


def test_similarity_zero_vector():
    vec1 = [0, 0]
    vec2 = [1, 2]
    score = cosine_similarity(vec1, vec2)
    assert score == 0.0