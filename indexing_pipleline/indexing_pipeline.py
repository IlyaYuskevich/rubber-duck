from haystack import Pipeline
from haystack.components.converters import HTMLToDocument
from weaviate import WeaviateClient
 
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder

from indexing_pipleline.file_content_reader import FileContentReader
from indexing_pipleline.weaviate_writer import WeaviateDocumentWriter

def init_indexing_pipleine(client: WeaviateClient) -> Pipeline:

    reader = FileContentReader()
    converter = HTMLToDocument()
    writer = WeaviateDocumentWriter(client)
    doc_embedder = FastembedDocumentEmbedder(
        model="BAAI/bge-small-en-v1.5",
        batch_size=256,
    )

    doc_embedder.warm_up()

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component(instance=reader, name="reader")
    indexing_pipeline.add_component(instance=converter, name="converter")
    indexing_pipeline.add_component(instance=doc_embedder, name="embedder")
    indexing_pipeline.add_component(instance=writer, name="writer")

    indexing_pipeline.connect("reader.streams", "converter.sources")
    indexing_pipeline.connect("converter.documents", "embedder.documents")
    indexing_pipeline.connect("embedder.documents", "writer.documents")
    return indexing_pipeline