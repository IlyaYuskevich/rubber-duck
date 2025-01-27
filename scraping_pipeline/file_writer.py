"""Haystack custom component writing the file to local storage."""

from pathlib import Path
from urllib.parse import urlparse
import typing as t

from haystack import component, logging
from haystack.dataclasses import ByteStream
from pydantic import HttpUrl
from haystack.components.converters.utils import get_bytestream_from_source
from bs4 import BeautifulSoup
from weaviate import WeaviateClient

from project_paths import BLOB_STORAGE
from document_store.queries import OnlineDocument, update_fetched_doc_meta, add_online_document
from weaviate.util import generate_uuid5
logger = logging.getLogger(__name__)


@component
class FileWriter:

    def __init__(self, client: WeaviateClient):
        self.client = client

    @component.output_types(documents_written=int, urls_added=int)
    def run(self, sources: t.List[ByteStream]):
        documents_written = 0
        urls_added = 0
        for source in sources:
            try:
                bytestream = get_bytestream_from_source(source=source)
            except Exception as e:
                logger.warning("Could not read {source}. Skipping it. Error: {error}", source=source, error=e)
                continue

            try:
                url = HttpUrl(bytestream.meta.get('url'))
                file_path = (BLOB_STORAGE / url.host / url.path[1:]).with_suffix('.html')
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(bytestream.data)

                extracted_urls = self.extract_urls(url, bytestream)
                
                uuid = generate_uuid5({'url': str(url)})
                print(f'\x1b[6;30;42m Url fetched {url} \x1b[0m')
                update_fetched_doc_meta(self.client, OnlineDocument(uuid=uuid, path=file_path, url=url, is_fetched=True))
                for extracted_url in extracted_urls:
                    added = add_online_document(self.client, extracted_url)
                    if added:
                        urls_added += 1
                        print(f'\x1b[5;30;46m Url added {extracted_url} \x1b[0m')

                documents_written += 1
            except Exception as conversion_e:
                logger.warning(
                    "Failed to extract text from {source}. Skipping it. Error: {error}",
                    source=source,
                    error=conversion_e,
                )
                continue
            
        return { "documents_written": documents_written, "urls_added": urls_added }
    
    def extract_urls(self, url: HttpUrl, bytestream: ByteStream) -> t.Set[str]:
        # Extract and normalize all links
        soup = BeautifulSoup(bytestream.data, "html.parser")
        scraped_urls = set()
        for anchor in soup.find_all("a", href=True):
            href = urlparse(anchor["href"])
            if href.netloc == url.host or len(href.netloc) == 0:
                normalized_url = HttpUrl.build(scheme=url.scheme, path=str(Path(href.path)).strip('/'), host=url.host)
                scraped_urls.add(str(normalized_url))
        return scraped_urls
