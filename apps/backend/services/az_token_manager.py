""" az_token_manager.py (Token Manager) """
import json

import asyncio
import subprocess
from datetime import datetime, timedelta

from apps.backend.core.config import settings

# verify to get token and auto refresh when expiration
class AzureTokenManager:
    def __init__(self):
        # initial variable
        self.token = None
        self.expire_on = None
        self.token_data = None
        self._lock = asyncio.Lock()

    def is_expired(self):
        if self.expire_on is None:
            return True
        # Refresh 5 minutes early to avoid edge cases
        return datetime.now() >= self.expire_on - timedelta(minutes=5)

    async def fetch_token(self):
        # throw to run in another thread if not -> subprocess will block other process in fastAPI
        loop = asyncio.get_event_loop()   
        result = await loop.run_in_executor(None, lambda: subprocess.run(
            [settings.AZ_PATH, "account", "get-access-token", "--resource", settings.AZ_WEBSV],
            capture_output=True,
            text=True,
            check=True
        ))

        self.token_data = json.loads(result.stdout)
        self.token = self.token_data["accessToken"]
        self.expire_on = datetime.fromisoformat(self.token_data["expiresOn"])
        return self.token_data
    
    # Use old or fetch new
    async def get_token(self):
        # prevent many user to refresh at the same time 
        async with self._lock:
            if self.is_expired():
                await self.fetch_token()
        return self.token
