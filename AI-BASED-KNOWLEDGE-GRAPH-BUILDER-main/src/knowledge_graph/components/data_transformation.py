import spacy
import re
import itertools
from neo4j import GraphDatabase
from pathlib import Path

from src.knowledge_graph.utils.common import read_json, write_json, read_yaml
from src.knowledge_graph.logger.logging import logger


class DataTransformation:

    def __init__(self, config):
        self.config = config
        self.docs = read_json(config.input_json)
        self.nlp = spacy.load("en_core_web_sm")

        self.entities = []
        self.relationships = []
        self.triples = []
        self.entity_map = {}

    def clean_text(self, text):
        return text.strip().lower().replace('"', '').replace("'", "")

    def clean_relation(self, text):
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        clean = clean.strip().replace(" ", "_").upper()
        return clean if clean else "RELATED_TO"

    # ---------- 1. ENTITY EXTRACTION ----------
    def extract_entities(self):
        logger.info("1. Extracting Entities...")

        for doc in self.docs:
            spacy_doc = self.nlp(doc["text"])

            for ent in spacy_doc.ents:
                key = f"{self.clean_text(ent.text)}_{ent.label_}"

                if key not in self.entity_map:
                    entity = {
                        "id": key,
                        "name": ent.text.strip(),
                        "label": ent.label_,
                        "doc_id": doc.get("id")
                    }
                    self.entity_map[key] = entity
                    self.entities.append(entity)

        write_json(self.config.entities_output, self.entities)
        logger.info(f"Extracted {len(self.entities)} unique entities.")

    # ---------- 2. RELATIONSHIP EXTRACTION ----------
    def extract_relationships(self):
        logger.info("2. Extracting Relationships...")
        seen = set()

        for doc in self.docs:
            spacy_doc = self.nlp(doc["text"])

            for sent in spacy_doc.sents:
                sent_entities = []

                for ent in sent.ents:
                    key = f"{self.clean_text(ent.text)}_{ent.label_}"
                    if key in self.entity_map:
                        sent_entities.append(self.entity_map[key])

                if len(sent_entities) < 2:
                    continue

                root_verb = "RELATED_TO"
                for token in sent:
                    if token.pos_ == "VERB":
                        root_verb = token.lemma_
                        break

                relation = self.clean_relation(root_verb)

                for src, tgt in itertools.combinations(sent_entities, 2):
                    if src["id"] == tgt["id"]:
                        continue

                    sig = f"{src['id']}|{relation}|{tgt['id']}"
                    if sig in seen:
                        continue

                    seen.add(sig)

                    self.relationships.append({
                        "relation_id": sig,
                        "subject_id": src["id"],
                        "subject_name": src["name"],
                        "relation": relation,
                        "object_id": tgt["id"],
                        "object_name": tgt["name"],
                        "sentence": sent.text.strip(),
                        "doc_id": doc.get("id")
                    })

        write_json(self.config.relationships_output, self.relationships)
        logger.info(f"Extracted {len(self.relationships)} relationships.")

    # ---------- 3. TRIPLE CREATION ----------
    def create_triples(self):
        logger.info("3. Creating Triples...")

        for rel in self.relationships:
            self.triples.append({
                "head_id": rel["subject_id"],
                "head_name": rel["subject_name"],
                "relation": rel["relation"],
                "tail_id": rel["object_id"],
                "tail_name": rel["object_name"]
            })

        write_json(self.config.triples_output, self.triples)
        logger.info(f"Generated {len(self.triples)} triples.")

    # ---------- 4. GRAPH CONSTRUCTION ----------
    def build_graph(self):
        logger.info("4. Building Graph in Neo4j...")

        cfg = read_yaml(Path("config/config.yaml"))
        neo4j_cfg = cfg["transform_data"]["neo4j"]

        uri = neo4j_cfg["uri"]
        username = neo4j_cfg["username"]
        password = neo4j_cfg["password"]

        driver = GraphDatabase.driver(uri, auth=(username, password))

        with driver.session(database="rag-kg-db") as session:
            for ent in self.entities:
                session.run(
                    """
                    MERGE (e:Entity {id: $id})
                    SET e.name = $name, e.type = $type
                    """,
                    id=ent["id"],
                    name=ent["name"],
                    type=ent["label"]
                )

            for t in self.triples:
                session.run(
                    """
                    MATCH (h:Entity {id: $hid})
                    MATCH (t:Entity {id: $tid})
                    MERGE (h)-[:RELATION {type: $rel}]->(t)
                    """,
                    hid=t["head_id"],
                    tid=t["tail_id"],
                    rel=t["relation"]
                )

        driver.close()
        logger.info("Graph Construction Completed Successfully.")

        
