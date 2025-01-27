"""Connect to document storage and init collections."""


from haystack_integrations.document_stores.weaviate.document_store import \
    WeaviateDocumentStore
from weaviate.classes.config import DataType, Property

# Create a collections for fetched files metadata in Weaviate
# (if not already created)
ONLINE_DOCUMENT_COLLECTION_NAME = "OnlineDocument"

def connect_to_document_store() -> WeaviateDocumentStore:
    document_store = WeaviateDocumentStore(url="http://localhost:8080")

    if not document_store.client.collections.exists(ONLINE_DOCUMENT_COLLECTION_NAME):
        document_store.client.collections.create(
            ONLINE_DOCUMENT_COLLECTION_NAME,
            properties=[
                Property(name="url", data_type=DataType.TEXT),
                Property(name="is_fetched", data_type=DataType.BOOL),
                Property(name="path", data_type=DataType.TEXT),
            ],
        )
    return document_store