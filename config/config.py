import json
import logging
import logging.config
import sys
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from typing import Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging(log_level: str = logging.INFO) -> None:
    """Configure logging for the ETL worker."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )

    sentry_sdk.init(
        dsn="http://eugene@sentry:9000/<PROJECT_ID>",
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,  # reduce in prod
        send_default_pii=False,
        environment="development",
    )

    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    )

    sentry_sdk.init(
        dsn="http://<PUBLIC_KEY>@sentry:9000/<PROJECT_ID>",
        integrations=[sentry_logging],
    )


class Settings(BaseSettings):
    def __init__(self, **values: Any):
        super().__init__(**values)
        setup_logging()

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    # Database settings
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_name: str = Field(..., alias="DB_NAME")
    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(5432, alias="DB_PORT")
    sql_options: str = Field("-c search_path=public,content", alias="SQL_OPTIONS")
    database_type: str = Field("postgres", alias="DATABASE_TYPE")
    batch_size: int = Field(1000, alias="BATCH_SIZE")

    # Elasticsearch settings
    elk_url: str = Field(..., alias="ELK_URL")
    elk_index: str = Field(..., alias="ELK_INDEX")
    elk_port: int = Field(9200, alias="ELK_PORT")

    # Other settings
    schema_file: str = Field(..., alias="SCHEMA_FILE")

    # Redis settings
    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")


settings = Settings()
