# Rubber Duck 🐥

**Rubber Duck** is a local-first AI companion powered by **DeepSeek-R1:7B** and RAG pipelines for scraping online documents, indexing, and querying a vector database. Perfect for developers who want an AI assistant tuned to their project or preferred documentation.

## Features
- **Local-first AI**: Privacy-focused, no cloud required.
- **RAG Pipelines**: Efficient document retrieval and context-aware querying.
- **Customizable Indexing**: Add your own files (e.g., docs, PDFs, repositories).

---

## Installation

### 1. Install [Ollama](https://ollama.com/library/deepseek-r1) and Pull DeepSeek-R1:7B:
Ensure you have `brew` installed on your system.

```bash
brew install ollama
ollama pull deepseek-r1:7b
```

### 2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/):
`uv` is a task runner for Python.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Usage

### Step 1: Preparing the Environment
Make sure that Ollama and Docker are running in your system. Then launch Weaviate (Vector database) container:

```bash
docker compose up -d
```

### Step 2: Scrape Online Documentation
Use the scraping pipeline to fetch online documentation and save it locally in a `blob_storage` directory.

```bash
uv run main.py scrape <url1> <url2> ...
```

You can also manually add additional files (e.g., PDFs) to the `blob_storage` directory.

---

### Step 3: Index Your Documents
Populate the vector database with embeddings for your documents. Optionally, include additional directories such as project repositories.

```bash
uv run main.py index [OPTIONAL] <dir1> <dir2>
```

---

### Step 4: Query with Context-Aware Responses
Ask your Rubber Duck anything about your indexed documents.

```bash
uv run main.py query "How to create error pages in Deno Fresh?"
```
