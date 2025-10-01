import pytest
from fastapi.testclient import TestClient
from neuralstark.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("neuralstark.main.Chroma")
def test_knowledge_base_search_with_filters(mock_chroma):
    mock_retriever = MagicMock()
    mock_chroma.return_value.as_retriever.return_value = mock_retriever
    
    client.post("/chat", json={"query": "test query", "start_date": "2023-01-01", "tags": ["test"]})
    
    mock_chroma.return_value.as_retriever.assert_called_with(
        search_kwargs={"filter": {"document_date": {"$gte": "2023-01-01"}, "tags": {"$contains": ["test"]}}})
