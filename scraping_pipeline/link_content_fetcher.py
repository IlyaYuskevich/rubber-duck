from concurrent.futures import ThreadPoolExecutor
import typing as t
from haystack import component, logging
from weaviate import WeaviateClient
from weaviate.util import generate_uuid5
from haystack.components.fetchers import LinkContentFetcher
from haystack.dataclasses.byte_stream import ByteStream

from document_store.queries import OnlineDocument, update_fetched_doc_meta
logger = logging.getLogger(__name__)


class CustomLinkContentFetcher(LinkContentFetcher):
    def __init__(self, client: WeaviateClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @component.output_types(streams=t.List[ByteStream])
    def run(self, urls: t.List[str]):
        """Override to properly handle 404."""
        streams: t.List[ByteStream] = []
        if not urls:
            return {"streams": streams}

        # don't use multithreading if there's only one URL
        if len(urls) == 1:
            stream_metadata, stream = self._fetch(urls[0])
            stream.meta.update(stream_metadata)
            stream.mime_type = stream.meta.get("content_type", None)
            streams.append(stream)
        else:
            with ThreadPoolExecutor() as executor:
                results = executor.map(self._fetch_with_exception_suppression, urls)

            for stream_metadata, stream in results:  # type: ignore
                if stream_metadata is not None and stream is not None:
                    stream.meta.update(stream_metadata)
                    stream.mime_type = stream.meta.get("content_type", None)
                    streams.append(stream)
                if stream_metadata.get("error", "").startswith("404 Client Error"):
                    url = str(stream_metadata.get('url'))
                    uuid = generate_uuid5({'url': url})
                    print(f'\x1b[0;37;41m Document does not exist {url} \x1b[0m')
                    update_fetched_doc_meta(self.client, OnlineDocument(uuid=uuid, url=url, is_fetched=True))

        return {"streams": streams}
    
    def _fetch_with_exception_suppression(self, url: str) -> t.Tuple[t.Optional[t.Dict[str, str]], t.Optional[ByteStream]]:
        if self.raise_on_failure:
            try:
                return self._fetch(url)
            except Exception as e:
                logger.warning("Error fetching {url}: {error}", url=url, error=str(e))
                return {"content_type": "Unknown", "url": url, "error": str(e)}, None
        else:
            return self._fetch(url)
