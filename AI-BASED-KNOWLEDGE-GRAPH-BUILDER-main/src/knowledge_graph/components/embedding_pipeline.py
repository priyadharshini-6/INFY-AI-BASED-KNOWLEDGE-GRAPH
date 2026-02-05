import os
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from src.knowledge_graph.utils.common import read_json, write_json, read_yaml
from src.knowledge_graph.logger.logging import logger


class EmbeddingPipeline:

    def __init__(self):
        cfg = read_yaml(Path("config/config.yaml"))

        self.input_json = cfg["pipeline_embedd"]["input_json"]

        self.chunk_size = cfg["pipeline_embedd"]["chunking"]["chunk_size"]
        self.chunk_overlap = cfg["pipeline_embedd"]["chunking"]["chunk_overlap"]

        self.model_name = cfg["pipeline_embedd"]["embedding_model"]["name"]
        self.embedding_dim = cfg["pipeline_embedd"]["embedding_model"]["embedding_dim"]

        self.index_path = cfg["pipeline_embedd"]["vector_store"]["index_path"]
        self.metadata_path = cfg["pipeline_embedd"]["vector_store"]["metadata_path"]

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        self.model = SentenceTransformer(self.model_name)

    # ------------------ TEXT CHUNKING ------------------

    def chunk_text(self, text):
        words = text.split()
        chunks = []

        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    # ------------------ MAIN PIPELINE ------------------

    def run(self):
        logger.info("Loading input documents...")
        docs = read_json(self.input_json)

        embeddings = []
        metadata = []

        logger.info("Chunking & embedding text...")

        for doc in docs:
            text = doc.get("text", "")
            chunks = self.chunk_text(text)

            for chunk in chunks:
                vector = self.model.encode(chunk)

                embeddings.append(vector)
                metadata.append({
                    "text": chunk,
                    "source_type": doc.get("source_type"),
                    "source_name": doc.get("source_name"),
                    "doc_id": doc.get("id")
                })

        if not embeddings:
            raise ValueError("No embeddings generated. Input data may be empty.")

        vectors = np.array(embeddings).astype("float32")

        logger.info("Building FAISS index...")
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(vectors)

        faiss.write_index(index, self.index_path)
        write_json(self.metadata_path, metadata)

        logger.info(f"FAISS index saved at {self.index_path}")
        logger.info(f"Metadata saved at {self.metadata_path}")
