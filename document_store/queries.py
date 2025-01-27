"""Module providing various queries for interaction with weaviate"""

import typing as t
from uuid import UUID
from weaviate import WeaviateClient
from document_store.store import ONLINE_DOCUMENT_COLLECTION_NAME
from pathlib import Path
from weaviate.util import generate_uuid5

from pydantic import BaseModel, HttpUrl


class OnlineDocument(BaseModel):
    uuid: UUID
    path: Path | None = None
    url: HttpUrl
    is_fetched: bool = False

def get_online_documents(client: WeaviateClient) -> t.List[OnlineDocument]:
    """Get online documents."""
    collection = client.collections.get(ONLINE_DOCUMENT_COLLECTION_NAME)
    return [OnlineDocument(uuid=file.uuid, url=file.properties["url"], path=file.properties["path"], is_fetched=file.properties["is_fetched"]) for file in collection.iterator()]

def update_fetched_doc_meta(client: WeaviateClient, metadata: OnlineDocument):
    """Adds fetched document metadata to DB."""
    collection = client.collections.get(ONLINE_DOCUMENT_COLLECTION_NAME)
    collection.data.update(uuid=metadata.uuid, properties={"is_fetched": True, "path": str(metadata.path)})

def add_online_document(client: WeaviateClient, url: str) -> t.Optional[OnlineDocument]:
    """Add Online Document to Weaviate as URL to fetch."""
    collection = client.collections.get(ONLINE_DOCUMENT_COLLECTION_NAME)
    uuid = generate_uuid5({"url": url})  # deterministic id
    if not collection.data.exists(uuid):
        collection.data.insert(uuid=uuid, properties={"url": url, "is_fetched": False})
        return OnlineDocument(uuid=uuid, url=url)

