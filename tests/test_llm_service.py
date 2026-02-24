from unittest.mock import patch
from app.services.llm import ask_llm


def test_ask_llm_success():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "Mock answer"
        }

        result = ask_llm("context", "question")

        assert result == "Mock answer"


def test_ask_llm_failure():
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Connection error")

        try:
            ask_llm("context", "question")
        except RuntimeError:
            assert True
