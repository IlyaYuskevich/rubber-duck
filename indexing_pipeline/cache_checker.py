import typing as t
from haystack import component
from document_store.queries import get_online_documents, add_online_document
from weaviate import WeaviateClient

@component
class CustomCacheChecker():

    def __init__(self, client: WeaviateClient):
        self.client = client

    @component.output_types(hits=t.List[str], misses=t.List[str])
    def run(self, items: t.List[str]):
        """Returns documents to fetch and fetched documents."""
        documents = get_online_documents(self.client)
        new_documents = [add_online_document(self.client, url) for url in items]

        return {
            "hits": [doc.url for doc in documents if doc.is_fetched],
            "misses": [doc.url for doc in documents if not doc.is_fetched] + [doc.url for doc in new_documents if doc],
        }
