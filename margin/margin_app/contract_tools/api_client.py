import httpx
import logging
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)

class BaseAPIClient:
   
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
       
        self.base_url = base_url
        self.headers = headers or {}

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 15
    ) -> Optional[Any]:
       
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=self.headers,
                    timeout=timeout,
                )
                response.raise_for_status()  
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {e.request.url}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {e.request.url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return None

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        
        return await self.request('GET', endpoint, params=params)
