from indexing_pipeline.web_scrapping import init_web_scrapping_pipeline
from document_store.store import connect_to_document_store

url_seed = ["https://fresh.deno.dev/docs/concepts/islands"]
weaviate_client = connect_to_document_store().client
web_scrapping_pipeline = init_web_scrapping_pipeline(weaviate_client)
urls_added = len(url_seed)
while urls_added:
    result = web_scrapping_pipeline.run(data={"cache_checker": {"items": url_seed}})
    urls_added = result['writer']['urls_added']
    print(result)
weaviate_client.close()
