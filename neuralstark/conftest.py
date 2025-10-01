import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_langchain_imports():
    with patch('langchain_huggingface.HuggingFaceEmbeddings') as mock_embeddings:
        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_llm:
            yield mock_embeddings, mock_llm