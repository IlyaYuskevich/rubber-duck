"""Module providing recoursive scrapping of selected urls. The result is saved in blob storage"""

from haystack import Pipeline
from weaviate import WeaviateClient
from scraping_pipeline.file_writer import FileWriter
from scraping_pipeline.cache_checker import CustomCacheChecker
from scraping_pipeline.link_content_fetcher import CustomLinkContentFetcher

def init_web_scrapping_pipeline(client: WeaviateClient) -> Pipeline:
    cache_checker = CustomCacheChecker(client)
    fetcher = CustomLinkContentFetcher(client, retry_attempts = 2, timeout = 3)
    writer = FileWriter(client)

    web_scrapping_pipeline = Pipeline()
    web_scrapping_pipeline.add_component(instance=cache_checker, name="cache_checker")
    web_scrapping_pipeline.add_component(instance=fetcher, name="fetcher")
    web_scrapping_pipeline.add_component(instance=writer, name="writer")

    web_scrapping_pipeline.connect("cache_checker.misses", "fetcher.urls")
    web_scrapping_pipeline.connect("fetcher.streams", "writer.sources")
    return web_scrapping_pipeline