from haystack import Pipeline
from weaviate import WeaviateClient
 
from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder

from query_pipeline.weaviate_retriever import WeaviateRetriever


def init_query_pipleine(client: WeaviateClient) -> Pipeline:

    text_embedder = FastembedTextEmbedder()
    retriever = WeaviateRetriever(client=client, top_k=10, distance=0.3)

    query_pipeline = Pipeline()
    query_pipeline.add_component("text_embedder", text_embedder)
    query_pipeline.add_component("retriever", retriever)

    query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    return query_pipeline