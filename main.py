import sys
import typing as t
import warnings

from scraping_pipeline.web_scrapping import init_web_scrapping_pipeline
from query_pipeline.query_pipeline import init_query_pipleine
from indexing_pipleline.indexing_pipeline import init_indexing_pipleine
from document_store.store import connect_to_document_store
from ollama import chat

from weaviate.collections.classes.data import DataObject

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)


def main():
    if len(sys.argv) < 2:
        print("Usage:\n")
        print(
            "Run scraping pipeline to download online documentation:\npython main.py scrape '<url1>' '<url2>' ... \n"
        )
        print(
            "Run indexing pipeline to populate vector database with document embeddings:\npython main.py index \n"
        )
        print("Run your query\n:python main.py query '<your_query>'\n")
        return
    if sys.argv[1] == "query" and len(sys.argv) < 3:
        print("Provide your query:\npython main.py query '<your_query>'")
        return
    if sys.argv[1] == "scrape" and len(sys.argv) < 3:
        print("Provide seed urls:\npython main.py scrape '<url1>' '<url2>' ... \n")
        return
    print("\033[1m\x1b[0;30;45m")
    print(f"========== Pipeline {sys.argv[1]} started ===========")
    print("\x1b[0m")
    with connect_to_document_store().client as weaviate_client:
        match sys.argv[1]:
            case "scrape":
                web_scrapping_pipeline = init_web_scrapping_pipeline(weaviate_client)
                url_seed = sys.argv[2:]
                urls_added = len(url_seed)
                while urls_added:
                    result = web_scrapping_pipeline.run(
                        data={"cache_checker": {"items": url_seed}}
                    )
                    urls_added = result["writer"]["urls_added"]
                    print(result["writer"])
            case "index":
                indexing_pipeline = init_indexing_pipleine(weaviate_client)
                result = indexing_pipeline.run(
                    data={
                        "reader": {
                            "directories": sys.argv[2:] if len(sys.argv) > 2 else []
                        }
                    }
                )
                print(result["writer"])
            case "query":
                query = sys.argv[2]
                query_pipeline = init_query_pipleine(weaviate_client)
                result = query_pipeline.run(data={"text_embedder": {"text": query}})
                prompt, _ = build_prompt(query, result["retriever"]["documents"])
                print("Documents included to the context:\n")
                for doc in result["retriever"]["documents"]:
                    print(doc.properties["path"] + "\n")
                # print(f'Prompt: {prompt}')
                stream = chat(
                    model="deepseek-r1:7b",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    # keep_alive=60,
                )
                for chunk in stream:
                    print(chunk["message"]["content"], end="", flush=True)

            case _:
                print("Invalid command. Use 'scrape', 'index', or 'query'.")

def build_prompt(question: str, documents: t.List[DataObject]) -> str:
    context = "\n".join([doc.properties.get("content") for doc in reversed(documents)])
    prompt = f"""
    Context: {context}

    Question: {question}

    """
    return prompt, context


if __name__ == "__main__":
    main()
