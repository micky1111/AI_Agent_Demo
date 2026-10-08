"""Loads the Markdown docs + price list CSV in data/, chunks them, embeds them
with OpenAI, and persists the result to a local Chroma vector store.

Run directly to (re)build the index: `uv run python src/ingest.py`
"""

import csv
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
COLLECTION_NAME = "company_brain"
EMBEDDING_MODEL = "text-embedding-3-small"


def load_markdown_documents() -> list[Document]:
    docs = []
    for path in sorted(DATA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def load_csv_documents() -> list[Document]:
    docs = []
    csv_path = DATA_DIR / "price_list.csv"
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            content = "\n".join(f"{key}: {value}" for key, value in row.items())
            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": "price_list.csv",
                        "row": i,
                        "unit_code": row.get("unit_code", ""),
                    },
                )
            )
    return docs


def chunk_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def build_index() -> Chroma:
    markdown_docs = load_markdown_documents()
    csv_docs = load_csv_documents()
    chunks = chunk_documents(markdown_docs) + csv_docs

    # Reset the collection first so re-running ingest rebuilds cleanly
    # instead of appending duplicate chunks on top of the previous run.
    client = chromadb.PersistentClient(path=str(PERSIST_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet on a first run

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIR),
    )

    print(
        f"Loaded {len(markdown_docs)} Markdown docs + {len(csv_docs)} CSV rows "
        f"-> {len(chunks)} chunks. Persisted to {PERSIST_DIR} "
        f"(collection '{COLLECTION_NAME}')."
    )
    return vectorstore


def main() -> None:
    build_index()

    try:
        from tools.firebase_ops import seed_apartments_from_csv

        created = seed_apartments_from_csv(DATA_DIR / "price_list.csv")
        print(
            f"Seeded {created} new apartment doc(s) into Firestore "
            "(existing docs — e.g. ones already updated live — were left untouched)."
        )
    except FileNotFoundError as e:
        print(f"Skipped Firestore seeding (no credentials yet): {e}")


if __name__ == "__main__":
    main()
