from fastapi import FastAPI
import time
import asyncio

from config import Settings


app = FastAPI()
settings = Settings()  # Load settings from .env file

@app.get("/")
def read_root():
    return {"message": "Agentic DE backend", "jira_email": settings.JIRA_EMAIL, "jira_domain": settings.JIRA_DOMAIN}

@app.get("/slow-sync")
def slow_sync():
    start_time = time.time()
    print(f"Start time: {start_time}")
    time.sleep(5)  # Simulate a slow synchronous operation
    time.sleep(5)
    end_time = time.time()
    print(f"End time: {end_time}")
    return {"elapsed_seconds": round(end_time - start_time, 2)}

@app.get("/slow-async")
async def slow_async():
    start_time = time.time()
    print(f"Start time: {start_time}")
    await asyncio.gather(asyncio.sleep(5), asyncio.sleep(5))  # Simulate a slow asynchronous operation
    end_time = time.time()
    print(f"End time: {end_time}")
    return {"elapsed_seconds": round(end_time - start_time, 2)}

