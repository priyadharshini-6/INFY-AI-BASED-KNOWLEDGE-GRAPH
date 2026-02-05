import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
from src.knowledge_graph.logger.logging import logger
from src.knowledge_graph.exception.exception import KGException
import sys
import pypdf


class DataIngestion:
    def __init__(self, config):
        self.config = config
        self.records = []
        self.counter = 1

    def _create_record(self, source_type, source_name, metadata, text):
        """Standardizes the record format."""
        if not text or not text.strip():
            return None

        record = {
            "id": self.counter,
            "source_type": source_type,
            "source_name": source_name,
            "metadata": metadata,
            "text": text.strip(),
            "ingestion_timestamp": datetime.utcnow().isoformat()
        }
        self.counter += 1
        return record

    def _row_to_text(self, row, columns):
        try:
            return ", ".join(
                [f"{col}: {val}" for col, val in zip(columns, row) if pd.notna(val)]
            )
        except Exception:
            return " ".join(map(str, row))

    # ---------- EMAIL INGESTION ----------
    def ingest_emails(self):
        logger.info("Starting Email Ingestion...")
        try:
            if not os.path.exists(self.config.email_dir):
                return

            files = [f for f in os.listdir(self.config.email_dir) if f.endswith(".txt")]

            for file in files:
                path = os.path.join(self.config.email_dir, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()

                    parts = content.split("\n\n", 1)
                    header_block = parts[0] if len(parts) > 0 else ""
                    body_text = parts[1] if len(parts) > 1 else content

                    headers = {}
                    for line in header_block.splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            headers[key.strip().lower()] = value.strip()

                    record = self._create_record(
                        source_type="email",
                        source_name=file,
                        metadata={
                            "from": headers.get("from"),
                            "to": headers.get("to"),
                            "date": headers.get("date"),
                            "subject": headers.get("subject"),
                            "file_path": os.path.abspath(path)
                        },
                        text=body_text
                    )
                    if record:
                        self.records.append(record)

                except Exception as e:
                    logger.warning(f"Failed to process email {file}: {e}")

        except Exception as e:
            logger.error(f"Critical error in email ingestion: {e}")

    # ---------- PDF INGESTION ----------
    def ingest_pdfs(self):
        logger.info("Starting PDF Ingestion...")
        try:
            if not os.path.exists(self.config.pdf_dir):
                return

            files = [f for f in os.listdir(self.config.pdf_dir) if f.endswith(".pdf")]

            for file in files:
                path = os.path.join(self.config.pdf_dir, file)
                try:
                    reader = pypdf.PdfReader(path)
                    text_content = []

                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_content.append(extracted)

                    full_text = "\n".join(text_content)

                    record = self._create_record(
                        source_type="pdf",
                        source_name=file,
                        metadata={
                            "pages": len(reader.pages),
                            "file_path": os.path.abspath(path)
                        },
                        text=full_text
                    )
                    if record:
                        self.records.append(record)

                except Exception as e:
                    logger.warning(f"Failed to process PDF {file}: {e}")

        except Exception as e:
            logger.error(f"Critical error in PDF ingestion: {e}")

    # ---------- CSV INGESTION ----------
    def ingest_csvs(self):
        logger.info("Starting CSV Ingestion...")
        try:
            if not os.path.exists(self.config.csv_dir):
                return

            files = [f for f in os.listdir(self.config.csv_dir) if f.endswith(".csv")]

            for file in files:
                path = os.path.join(self.config.csv_dir, file)
                try:
                    for chunk in pd.read_csv(path, chunksize=1000):
                        columns = list(chunk.columns)
                        for row in chunk.values:
                            text = self._row_to_text(row, columns)
                            record = self._create_record(
                                source_type="csv",
                                source_name=file,
                                metadata={
                                    "columns": columns,
                                    "file_path": os.path.abspath(path)
                                },
                                text=text
                            )
                            if record:
                                self.records.append(record)

                except Exception as e:
                    logger.warning(f"Failed to process CSV {file}: {e}")

        except Exception as e:
            logger.error(f"Critical error in CSV ingestion: {e}")

    # ---------- DATABASE INGESTION ----------
    def ingest_db(self):
        logger.info("Starting Database Ingestion...")
        if not os.path.exists(self.config.db_path):
            return

        conn = None
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for (table_name,) in tables:
                try:
                    for chunk in pd.read_sql_query(
                        f"SELECT * FROM {table_name}", conn, chunksize=1000
                    ):
                        columns = list(chunk.columns)
                        for row in chunk.values:
                            text = self._row_to_text(row, columns)
                            record = self._create_record(
                                source_type="database",
                                source_name=table_name,
                                metadata={
                                    "columns": columns,
                                    "db_path": os.path.abspath(self.config.db_path)
                                },
                                text=text
                            )
                            if record:
                                self.records.append(record)

                except Exception as e:
                    logger.warning(f"Failed to ingest table {table_name}: {e}")

        except Exception as e:
            logger.error(f"Database connection error: {e}")
        finally:
            if conn:
                conn.close()

    # ---------- MAIN PIPELINE ----------
    def ingest(self):
        try:
            logger.info(f">>> Ingestion Started at {datetime.now()}")

            self.ingest_emails()
            self.ingest_pdfs()
            self.ingest_csvs()
            self.ingest_db()

            # ✅ SAFE JSON WRITE (THIS FIXES YOUR ERROR)
            os.makedirs(os.path.dirname(self.config.output_json), exist_ok=True)
            with open(self.config.output_json, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)

            logger.info(
                f"<<< Ingestion Completed. Total Records: {len(self.records)}"
            )

        except Exception as e:
            raise KGException(e, sys)
