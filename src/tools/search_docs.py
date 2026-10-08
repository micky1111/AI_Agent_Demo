"""Tool: semantic search over the Chroma index built by src/ingest.py.

Run directly to try a query: `uv run python src/tools/search_docs.py "<question>"`
"""

import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

PERSIST_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "company_brain"
EMBEDDING_MODEL = "text-embedding-3-small"

DEMO_QUERY = "What is the cancellation policy?"


def _get_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
    )


def search_docs(query: str, k: int = 4) -> list[dict]:
    vectorstore = _get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return [
        {"source": doc.metadata.get("source"), "content": doc.page_content}
        for doc in results
    ]


def main() -> None:
    query = " ".join(sys.argv[1:]) or DEMO_QUERY
    print(f"Query: {query}\n")
    for i, result in enumerate(search_docs(query), start=1):
        print(f"[{i}] ({result['source']})\n{result['content']}\n")


if __name__ == "__main__":
    main()
