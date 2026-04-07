from email.policy import HTTP

import httpx

from config import Settings

class JiraClient:
    # Accept Settings instead of three separate args — cleaner interface:
    # def __init__(self, email: str, api_token: str, domain: str):
    def __init__(self, settings: Settings):
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        self.domain = settings.JIRA_DOMAIN

        self._client = httpx.AsyncClient(
            base_url=f"https://{self.domain}.atlassian.net", # base_url: prepended to all relative paths (e.g., "/rest/api/3/myself")
            auth=httpx.BasicAuth(self.email, self.api_token),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }    
        )

    async def ping(self) -> int:
        try:
            response = await self._client.get("/rest/api/3/myself")
            response.raise_for_status() 
            return response.status_code
        except httpx.HTTPError as e:
            print(f"Jira API ping failed: {e}")
            # If the error is a connection failure (e.g. bad domain), 
            # there's no response object at all — this will crash with UnboundLocalError.

            # A 401 Unauthorized — if your .env credentials are incorrect
            return -1  

    async def close(self) -> None:
        await self._client.aclose()

