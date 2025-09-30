#!/usr/bin/env python3
"""
Async wrapper for PropellerAds Professional Client
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from .client import PropellerAdsClient


class AsyncPropellerAdsClient:
    """
    Async wrapper for PropellerAdsClient.

    This class provides async/await support by running synchronous operations
    in a thread pool executor.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize async client.

        Args:
            api_key (str): PropellerAds API key
            **kwargs: Additional arguments passed to PropellerAdsClient
        """
        self._sync_client = PropellerAdsClient(api_key, **kwargs)
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self):
        """Close the async client and cleanup resources"""
        self._sync_client.close()
        self._executor.shutdown(wait=True)

    async def get_balance(self) -> Any:
        """Get account balance asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, 
            self._sync_client.get_balance
        )

    async def get_campaigns(self, **kwargs) -> List[Any]:
        """Get campaigns asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self._sync_client.get_campaigns(**kwargs)
        )

    async def get_statistics(self, **kwargs) -> Any:
        """Get statistics asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self._sync_client.get_statistics(**kwargs)
        )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._sync_client.health_check
        )

    # Delegate other methods to sync client
    def __getattr__(self, name):
        """Delegate unknown attributes to sync client"""
        attr = getattr(self._sync_client, name)

        if callable(attr):
            async def async_wrapper(*args, **kwargs):
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    self._executor,
                    lambda: attr(*args, **kwargs)
                )
            return async_wrapper

        return attr

