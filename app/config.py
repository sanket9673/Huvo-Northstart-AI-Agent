import os
from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the absolute path to the .env file in the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_file_path = os.path.join(root_dir, ".env")

class Settings(BaseSettings):
    GROQ_API_KEY: str = Field(default="")
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_BASE_URL: Optional[str] = Field(default=None)
    LLM_MODEL: str = Field(default="llama-3.3-70b-versatile")
    PROJECT_NAME: str = Field(default="Northstar Homes AI Agent")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    APP_ENV: str = Field(default="development")

    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(env_file=env_file_path, extra="ignore")

    @model_validator(mode="after")
    def set_openai_base_url(self) -> 'Settings':
        if self.GROQ_API_KEY:
            if not self.OPENAI_BASE_URL:
                self.OPENAI_BASE_URL = "https://api.groq.com/openai/v1"
            if self.LLM_MODEL == "llama-3.3-70b-versatile" or self.LLM_MODEL == "llama-3.1-8b-instant" or not self.LLM_MODEL:
                self.LLM_MODEL = "openai/gpt-oss-20b"
        return self

# Global settings instance
settings = Settings()


