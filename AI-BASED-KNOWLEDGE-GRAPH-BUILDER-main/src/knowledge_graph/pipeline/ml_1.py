from src.knowledge_graph.config.configuration import ConfigManager
from src.knowledge_graph.components.ingestion_data import DataIngestion
from src.knowledge_graph.exception.exception import KGException
import sys


class DataIngestionTrainingPipeline:
    def __init__(self):
        pass

    def initiate_ingestion_data(self):
        try:
            print(">>> Data Ingestion started")

            config = ConfigManager()
            di_config = config.get_ingestion_data_config()

            ingestion = DataIngestion(di_config)
            ingestion.ingest()

            print(">>> Data Ingestion completed successfully")

        except Exception as e:
            raise KGException(e, sys)


# ✅ THIS IS THE MISSING PART
if __name__ == "__main__":
    pipeline = DataIngestionTrainingPipeline()
    pipeline.initiate_ingestion_data()
