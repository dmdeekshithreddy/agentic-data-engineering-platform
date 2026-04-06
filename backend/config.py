from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env")

    # Jira
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_DOMAIN: str
