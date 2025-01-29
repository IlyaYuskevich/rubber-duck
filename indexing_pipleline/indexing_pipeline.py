from haystack import Pipeline
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.converters import HTMLToDocument, PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder
from haystack.components.preprocessors import DocumentCleaner

from weaviate import WeaviateClient

from indexing_pipleline.file_content_reader import FileContentReader
from indexing_pipleline.weaviate_writer import WeaviateDocumentWriter

def init_indexing_pipleine(client: WeaviateClient) -> Pipeline:

    reader = FileContentReader()
    html_converter = HTMLToDocument()
    pdf_converter = PyPDFToDocument()
    joiner = DocumentJoiner(join_mode="concatenate")
    router = FileTypeRouter(mime_types=["text/html", "text/plain", "application/pdf"])
    
    writer = WeaviateDocumentWriter(client)
    doc_embedder = FastembedDocumentEmbedder(
        model="BAAI/bge-small-en-v1.5",
        batch_size=256,
    )
    splitter = DocumentSplitter(split_by="sentence", split_length=40, split_overlap=0, split_threshold=3)
    cleaner = DocumentCleaner()

    doc_embedder.warm_up()

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component(instance=reader, name="reader")
    indexing_pipeline.add_component(instance=router, name="router")
    indexing_pipeline.add_component(instance=html_converter, name="html_converter")
    indexing_pipeline.add_component(instance=pdf_converter, name="pdf_converter")
    indexing_pipeline.add_component(instance=joiner, name="joiner")
    indexing_pipeline.add_component(instance=cleaner, name="cleaner")
    indexing_pipeline.add_component(instance=splitter, name="splitter")
    indexing_pipeline.add_component(instance=doc_embedder, name="embedder")
    indexing_pipeline.add_component(instance=writer, name="writer")

    indexing_pipeline.connect("reader.streams", "router.sources")

    indexing_pipeline.connect("router.text/html", "html_converter.sources")
    indexing_pipeline.connect("html_converter.documents", "joiner.documents")

    indexing_pipeline.connect("router.application/pdf", "pdf_converter.sources")
    indexing_pipeline.connect("pdf_converter.documents", "joiner.documents")

    indexing_pipeline.connect("joiner.documents", "cleaner.documents")
    indexing_pipeline.connect("cleaner.documents", "splitter.documents")
    indexing_pipeline.connect("splitter.documents", "embedder.documents")
    indexing_pipeline.connect("embedder.documents", "writer.documents")
    return indexing_pipeline