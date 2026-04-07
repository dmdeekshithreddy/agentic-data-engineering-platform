from ast import If

from pydantic_settings import BaseSettings, SettingsConfigDict



# `BaseSettings` is not a normal Python class. It comes from Pydantic and overrides how `__init__` works.
# Settings class inherits from BaseSettings, which means it gets all the special behavior of loading values from environment variables and .env files.

# 2. What happens when you call Settings()
# `BaseSettings` adds a special step before __init__ runs:

# 1. It looks at each field declared in your class (JIRA_EMAIL, JIRA_API_TOKEN, JIRA_DOMAIN)
# 2. For each field, it searches for a value in this order:
#       Constructor arguments — Settings(JIRA_EMAIL="x") (highest priority)
#       Environment variables — checks os.environ["JIRA_EMAIL"]
#       .env file — reads the file specified in model_config (your ../.env)
# If found, it assigns the value to that field
# If not found anywhere and no default exists — it raises a ValidationError at runtime

# Pydantic matches the field name (JIRA_EMAIL) to the env var name (JIRA_EMAIL) — case-insensitive by default.
# That's why it works without passing any arguments.

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env")

    # Jira
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_DOMAIN: str
