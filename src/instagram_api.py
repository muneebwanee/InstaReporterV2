import aiohttp
import asyncio
import json
import random
from typing import Optional
from .utils import print_error, print_status

class InstagramAPI:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.api_url = "https://www.instagram.com"
        self.headers = self._get_default_headers()
        
    def _get_default_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Instagram-AJAX": "1",
            "X-Requested-With": "XMLHttpRequest",
            "DNT": "1",
            "Connection": "keep-alive",
        }

    async def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None):
        proxy = await self.proxy_manager.get_proxy()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    f"{self.api_url}/{endpoint}",
                    json=data if method == "POST" else None,
                    headers=self.headers,
                    proxy=proxy
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        print_error("Rate limit reached. Switching proxy...")
                        await self.proxy_manager.remove_proxy(proxy)
                        return await self._make_request(method, endpoint, data)
                    else:
                        print_error(f"Request failed with status {response.status}")
                        return None
            except Exception as e:
                print_error(f"Request error: {str(e)}")
                await self.proxy_manager.remove_proxy(proxy)
                return None

    async def report_profile(self, username: str, reason: str) -> bool:
        print_status(f"Reporting profile: {username}")
        
        data = {
            "source_name": "profile",
            "reason_id": self._get_reason_id(reason),
            "username": username
        }
        
        result = await self._make_request(
            "POST",
            "users/report/",
            data
        )
        
        return result and result.get("status") == "ok"

    async def report_post(self, post_url: str, reason: str) -> bool:
        print_status(f"Reporting post: {post_url}")
        
        # Extract post ID from URL
        post_id = self._extract_post_id(post_url)
        if not post_id:
            print_error("Invalid post URL")
            return False
            
        data = {
            "source_name": "media",
            "reason_id": self._get_reason_id(reason),
            "media_id": post_id
        }
        
        result = await self._make_request(
            "POST",
            "media/report/",
            data
        )
        
        return result and result.get("status") == "ok"

    def _get_reason_id(self, reason: str) -> int:
        reason_map = {
            "spam": 1,
            "abuse": 2,
            "other": 3
        }
        return reason_map.get(reason.lower(), 3)

    def _extract_post_id(self, url: str) -> Optional[str]:
        try:
            # Example URL: https://www.instagram.com/p/ABC123/
            return url.split("/p/")[1].split("/")[0]
        except:
            return None
