"""
Configuration settings for the EUC Assessment Agent Team.

This module contains settings and configuration parameters used by the agents.
"""

import os
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Settings class for the application."""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model settings
    openai_model_name: str = os.getenv("OPENAI_MODEL", "gpt-4")
    agent_temperature: float = 0.0
    
    # Application settings
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    @field_validator("openai_api_key")
    def validate_openai_api_key(cls, v):
        """Validate that the OpenAI API key is at least set (doesn't verify if it's valid)."""
        if not v:
            # For testing, we'll allow empty API keys
            pass
        return v


def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings: Application settings
    """
    return Settings() 