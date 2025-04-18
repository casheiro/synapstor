import os
from unittest.mock import patch

from synapstor.settings import (
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
)


class TestQdrantSettings:
    """Tests for the QdrantSettings class."""

    def test_default_values(self):
        """Tests if default values are correctly defined when no environment variables are provided."""
        with patch.dict(os.environ, {}, clear=True):
            settings = QdrantSettings()
            assert settings.location is None
            assert settings.collection_name is None
            assert settings.api_key is None
            assert settings.local_path is None
            assert settings.search_limit is None
            assert settings.read_only is False

    @patch.dict(
        os.environ,
        {"QDRANT_URL": "http://localhost:6333", "COLLECTION_NAME": "test_collection"},
        clear=True,
    )
    def test_minimal_config(self):
        """Tests loading minimal configuration from environment variables."""
        settings = QdrantSettings()
        assert settings.location == "http://localhost:6333"
        assert settings.collection_name == "test_collection"
        assert settings.api_key is None

    @patch.dict(
        os.environ,
        {
            "QDRANT_URL": "http://qdrant.example.com",
            "QDRANT_API_KEY": "test-api-key",
            "COLLECTION_NAME": "example_collection",
            "QDRANT_SEARCH_LIMIT": "5",
            "QDRANT_READ_ONLY": "true",
        },
        clear=True,
    )
    def test_full_config(self):
        """Tests loading full configuration from environment variables."""
        settings = QdrantSettings()
        assert settings.location == "http://qdrant.example.com"
        assert settings.api_key == "test-api-key"
        assert settings.collection_name == "example_collection"
        assert settings.search_limit == 5
        assert settings.read_only is True

    @patch.dict(
        os.environ,
        {"QDRANT_LOCAL_PATH": "/path/to/local/qdrant"},
        clear=True,
    )
    def test_local_qdrant(self):
        """Tests loading local Qdrant configuration."""
        settings = QdrantSettings()
        assert settings.location is None
        assert settings.local_path == "/path/to/local/qdrant"


class TestEmbeddingProviderSettings:
    """Tests for the EmbeddingProviderSettings class."""

    def test_default_values(self):
        """Tests if default values are correctly defined when no environment variables are provided."""
        with patch.dict(os.environ, {}, clear=True):
            settings = EmbeddingProviderSettings()
            assert settings.model_name == "sentence-transformers/all-MiniLM-L6-v2"

    @patch.dict(
        os.environ,
        {"EMBEDDING_MODEL": "openai/text-embedding-ada-002"},
        clear=True,
    )
    def test_custom_model(self):
        """Tests loading a custom model from environment variable."""
        settings = EmbeddingProviderSettings()
        assert settings.model_name == "openai/text-embedding-ada-002"


class TestToolSettings:
    """Tests for the ToolSettings class."""

    def test_default_values(self):
        """Tests if default values are correctly defined when no environment variables are provided."""
        with patch.dict(os.environ, {}, clear=True):
            settings = ToolSettings()
            # We only check that default values are non-empty strings
            assert isinstance(settings.tool_store_description, str)
            assert len(settings.tool_store_description) > 0
            assert isinstance(settings.tool_find_description, str)
            assert len(settings.tool_find_description) > 0

    @patch.dict(
        os.environ,
        {"TOOL_STORE_DESCRIPTION": "Custom store description"},
        clear=True,
    )
    def test_custom_store_description(self):
        """Tests loading a custom store tool description from environment variable."""
        settings = ToolSettings()
        # We check that the custom value was loaded correctly
        assert settings.tool_store_description == "Custom store description"
        # We only check that default value is a non-empty string
        assert isinstance(settings.tool_find_description, str)
        assert len(settings.tool_find_description) > 0

    @patch.dict(
        os.environ,
        {"TOOL_FIND_DESCRIPTION": "Custom find description"},
        clear=True,
    )
    def test_custom_find_description(self):
        """Tests loading a custom find tool description from environment variable."""
        settings = ToolSettings()
        # We only check that default value is a non-empty string
        assert isinstance(settings.tool_store_description, str)
        assert len(settings.tool_store_description) > 0
        # We check that the custom value was loaded correctly
        assert settings.tool_find_description == "Custom find description"

    @patch.dict(
        os.environ,
        {
            "TOOL_STORE_DESCRIPTION": "Custom store description",
            "TOOL_FIND_DESCRIPTION": "Custom find description",
        },
        clear=True,
    )
    def test_both_custom_descriptions(self):
        """Tests loading both custom descriptions from environment variables."""
        settings = ToolSettings()
        assert settings.tool_store_description == "Custom store description"
        assert settings.tool_find_description == "Custom find description"
