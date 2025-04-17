from synapstor.embeddings.base import EmbeddingProvider
from synapstor.embeddings.types import EmbeddingProviderType
from synapstor.settings import EmbeddingProviderSettings


def create_embedding_provider(settings: EmbeddingProviderSettings) -> EmbeddingProvider:
    """
    Cria um provedor de embeddings baseado no tipo especificado.
    :param settings: As configurações para o provedor de embeddings.
    :return: Uma instância do provedor de embeddings especificado.
    """
    if settings.provider_type == EmbeddingProviderType.FASTEMBED:
        from synapstor.embeddings.fastembed import FastEmbedProvider

        return FastEmbedProvider(settings.model_name)
    else:
        raise ValueError(f"Provedor de embeddings não suportado: {settings.provider_type}")
