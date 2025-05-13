from pydantic_settings import BaseSettings
from pydantic import Field, Json
from typing import List

class Settings(BaseSettings):
    cohere_api_key: str = Field(..., validation_alias="COHERE_API_KEY")
    app_env: str = Field("dev", validation_alias="APP_ENV")
    allowed_file_types: List[str] = Field(
        ["application/pdf"], 
        validation_alias="ALLOWED_FILE_TYPES",
        json_schema_extra={"example": '["application/pdf"]'}
    )
    max_file_size: int = Field(
        5242880,  # 5MB
        validation_alias="MAX_FILE_SIZE",
        json_schema_extra={"example": 5242880}
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()