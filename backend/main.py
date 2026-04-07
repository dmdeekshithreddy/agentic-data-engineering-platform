from fastapi import FastAPI
import time
import asyncio
from contextlib import asynccontextmanager

from config import Settings
from services.jira_client import JiraClient



@asynccontextmanager
async def lifecycle_manager(app: FastAPI):
    settings = Settings()  # Load settings from .env file
    client = JiraClient(settings=settings)

    app.state.jira_client = client  # Store the client in app state for access in routes
    yield # Control returns here after the app starts up
    await client.close()

app = FastAPI(lifespan=lifecycle_manager)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Agentic Data Engineer Platform!"}

@app.get("/ping")
async def read_jira():
    status_code = await app.state.jira_client.ping()
    return {"status code": status_code} # return type should always be a dict


