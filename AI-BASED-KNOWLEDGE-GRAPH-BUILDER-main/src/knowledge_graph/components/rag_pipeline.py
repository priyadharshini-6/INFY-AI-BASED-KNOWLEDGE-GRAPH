import json
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

from src.knowledge_graph.utils.common import read_yaml
from src.knowledge_graph.logger.logging import logger


class RAGPipeline:
    def __init__(self):
        cfg = read_yaml(Path("config/config.yaml"))

        self.index_path = cfg["rag"]["faiss"]["index_path"]
        self.metadata_path = cfg["rag"]["faiss"]["metadata_path"]
        self.top_k = cfg["rag"]["faiss"]["top_k"]

        self.model = SentenceTransformer(
            cfg["pipeline_embedd"]["embedding_model"]["name"]
        )

        self.index = faiss.read_index(self.index_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        logger.info("RAGPipeline initialized successfully")

    def answer(self, question: str):
        query_vec = self.model.encode(question).astype("float32").reshape(1, -1)
        _, indices = self.index.search(query_vec, self.top_k)

        chunks = [self.metadata[i] for i in indices[0]]

        answer = "\n".join(c["text"] for c in chunks[:3])
        sources = list(
            set(f"{c['source_type']} → {c['source_name']}" for c in chunks)
        )

        return answer, sources
