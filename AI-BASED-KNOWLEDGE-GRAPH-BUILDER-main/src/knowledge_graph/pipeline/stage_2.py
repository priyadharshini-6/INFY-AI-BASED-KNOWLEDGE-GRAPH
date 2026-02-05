from src.knowledge_graph.config.configuration import ConfigManager
from src.knowledge_graph.components.transform_data import DataTransformation
from src.knowledge_graph.exception.exception import KGException
import sys


class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_transform_data(self):
        try:
            print(">>> Data Transformation started")

            config_manager = ConfigManager()
            dt_config = config_manager.get_transform_data_config()

            obj = DataTransformation(dt_config)

            obj.extract_entities()
            print(">>> Entities extracted")

            obj.extract_relationships()
            print(">>> Relationships extracted")

            obj.create_triples()
            print(">>> Triples created")

            obj.build_graph()
            print(">>> Knowledge graph built in Neo4j")

            print(">>> Data Transformation completed successfully")

        except Exception as e:
            raise KGException(e, sys)


# ✅ THIS IS THE MISSING PART
if __name__ == "__main__":
    pipeline = DataTransformationTrainingPipeline()
    pipeline.initiate_transform_data()
