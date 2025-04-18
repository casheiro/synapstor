from synapstor.embeddings.base import EmbeddingProvider
from synapstor.embeddings.types import EmbeddingProviderType
from synapstor.settings import EmbeddingProviderSettings


def create_embedding_provider(settings: EmbeddingProviderSettings) -> EmbeddingProvider:
    """
    Creates an embedding provider based on the specified type.
    :param settings: The settings for the embedding provider.
    :return: An instance of the specified embedding provider.
    """
    if settings.provider_type == EmbeddingProviderType.FASTEMBED:
        from synapstor.embeddings.fastembed import FastEmbedProvider

        return FastEmbedProvider(settings.model_name)
    else:
        raise ValueError(f"Unsupported embedding provider: {settings.provider_type}")
