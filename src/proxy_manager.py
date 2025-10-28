import aiohttp
import asyncio
from typing import List, Optional
from .utils import print_status, print_error
import aiofiles

class ProxyManager:
    def __init__(self, proxy_file: Optional[str] = None):
        self.proxy_file = proxy_file
        self.proxies: List[str] = []
        self.working_proxies: List[str] = []
        self.current_index = 0

    async def load_proxies(self):
        """Load and validate proxies"""
        if self.proxy_file:
            await self._load_from_file()
        else:
            await self._load_from_api()
            
        print_status(f"Validating {len(self.proxies)} proxies...")
        await self._validate_proxies()
        print_status(f"Found {len(self.working_proxies)} working proxies")

    async def _load_from_file(self):
        """Load proxies from file"""
        try:
            async with aiofiles.open(self.proxy_file, 'r') as f:
                content = await f.read()
                self.proxies = [p.strip() for p in content.split('\n') if p.strip()]
        except Exception as e:
            print_error(f"Error loading proxy file: {str(e)}")
            self.proxies = []

    async def _load_from_api(self):
        """Load proxies from public APIs"""
        apis = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
        ]
        
        for api in apis:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api) as response:
                        if response.status == 200:
                            content = await response.text()
                            new_proxies = [p.strip() for p in content.split('\n') if p.strip()]
                            self.proxies.extend(new_proxies)
            except Exception as e:
                print_error(f"Error fetching proxies from {api}: {str(e)}")

    async def _validate_proxies(self):
        """Validate proxies in parallel"""
        tasks = []
        for proxy in self.proxies:
            tasks.append(self._validate_proxy(proxy))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.working_proxies = [
            proxy for proxy, result in zip(self.proxies, results)
            if isinstance(result, bool) and result
        ]

    async def _validate_proxy(self, proxy: str) -> bool:
        """Validate single proxy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://www.instagram.com",
                    proxy=f"http://{proxy}",
                    timeout=10
                ) as response:
                    return response.status == 200
        except:
            return False

    async def get_proxy(self) -> Optional[str]:
        """Get next working proxy"""
        if not self.working_proxies:
            return None
            
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return f"http://{proxy}"

    async def remove_proxy(self, proxy: str):
        """Remove non-working proxy"""
        try:
            proxy = proxy.replace("http://", "").replace("https://", "")
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
        except:
            pass
