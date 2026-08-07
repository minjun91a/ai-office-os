import chromadb
from sentence_transformers import SentenceTransformer

_client = chromadb.HttpClient(host="localhost", port=8001)
_collection = _client.get_or_create_collection(name="documents")

_embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = _embedding_model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def add_chunks(document_id: int, chunks: list[str]) -> None:
    if not chunks:
        return

    embeddings = embed_texts(chunks)
    ids = [f"doc{document_id}-chunk{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]

    _collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )


def delete_document_chunks(document_id: int) -> None:
    _collection.delete(where={"document_id": document_id})