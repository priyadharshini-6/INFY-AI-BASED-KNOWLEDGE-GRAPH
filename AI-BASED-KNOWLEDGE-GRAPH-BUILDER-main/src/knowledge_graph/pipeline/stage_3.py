from src.py.components.pipeline_embedd import EmbeddingPipeline

from src.knowledge_graph.logger.logging import logger
from src.knowledge_graph.exception.exception import KGException
import sys


class EmbeddingTrainingPipeline:
    def __init__(self):
        pass

    def initiate_pipeline_embedd(self):
        try:
            logger.info(">>> Embedding pipeline started")
            pipeline = EmbeddingPipeline()
            pipeline.run()
            logger.info(">>> Embedding pipeline completed successfully")
        except Exception as e:
            raise KGException(e, sys)


if __name__ == "__main__":
    pipeline = EmbeddingTrainingPipeline()
    pipeline.initiate_pipeline_embedd()
