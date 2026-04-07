from fastapi import FastAPI
import time
import asyncio
from contextlib import asynccontextmanager

from config import Settings
from services.jira_client import JiraClient

app = FastAPI()


settings = Settings()  # Load settings from .env file

# create the reat api connection pool to jira, and reuse it for all requests. 
# This is more efficient than creating a new client for each request.
# this piece of code should not be inside the endpoint function like below, otherwise it will create a new client for each request, 
# which is inefficient and can lead to connection issues.
# """
# @app.get("/ping")
# async def read_jira():
#     client = JiraClient(settings=settings)
#     status_code = await client.ping()
#     await client.close()
#     return {"status code": status_code} # return type should always be a dict
# """

@asynccontextmanager
async def lifecycle_manager():

    client = JiraClient(settings=settings)
    yield client
    await client.close()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Agentic Data Engineer Platform!"}

@app.get("/ping")
async def read_jira():
    status_code = await client.ping()
    await client.close()
    return {"status code": status_code} # return type should always be a dict


