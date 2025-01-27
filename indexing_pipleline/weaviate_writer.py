import typing as t
from haystack import component, Document
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient

from document_store.store import DOCUMENTS_WITH_EMBEDDING


@component
class WeaviateDocumentWriter:
    def __init__(self, client: WeaviateClient):
        self.client = client

    @component.output_types(documents_written=int)
    def run(self, documents: t.List[Document]):
        """Writes documents to Weaviate vector database."""
        documents_written = 0

        for document in documents:
            uuid = generate_uuid5(document.id)
            collection = self.client.collections.get(DOCUMENTS_WITH_EMBEDDING)
            print(document.embedding)
            if collection.data.exists(uuid=uuid):
                continue
            collection.data.insert(
                uuid=uuid,
                properties={"content": document.content, "path": document.meta["path"]},
                vector=document.embedding,
            )
            documents_written += 1

        return {
            "documents_written": documents_written,
        }
