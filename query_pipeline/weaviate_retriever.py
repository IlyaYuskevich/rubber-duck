import typing as t

from haystack import component, Document
from weaviate import WeaviateClient
from weaviate.classes.query import MetadataQuery

from document_store.store import DOCUMENTS_WITH_EMBEDDING


@component
class WeaviateRetriever:
    def __init__(self, client: WeaviateClient, distance: float = 0.2, top_k: int = 10):
        self.client = client
        self.top_k = top_k
        self.distance = distance

    @component.output_types(documents=t.List[Document])
    def run(self, query_embedding: t.List[float]):
        """Searches top_k closest documents to a query."""
        collection = self.client.collections.get(DOCUMENTS_WITH_EMBEDDING)
        resp = collection.query.near_vector(
            near_vector=query_embedding,
            limit=self.top_k,
            distance=self.distance,
            return_metadata=MetadataQuery(distance=True),
        )
        return {
            "documents": resp.objects,
        }
