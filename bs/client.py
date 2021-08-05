from .http import HTTPClient, BasicThrottler, BatchThrottler
import logging
import asyncio
from typing import Type, Union

KEY_MINIMUM, KEY_MAXIMUM = 1, 10
LOG = logging.getLogger(__name__)


class Client:
    """Client connection to interact with the api."""

    def __init__(
            self,
            *,
            key_count: int = 1,
            key_names: str = "Created with bs.py Client",
            throttle_limit: int = 10,
            loop: asyncio.AbstractEventLoop = None,
            correct_tags: bool = True,
            throttler: Type[Union[BasicThrottler, BatchThrottler]] = BasicThrottler,
            connector=None,
            timeout: float = 30.0,
            cache_max_size: int = 10000,
            stats_max_size: int = 1000,
            **_,
    ):
        self.loop = loop or asyncio.get_event_loop()

        self.correct_key_count = max(min(KEY_MAXIMUM, key_count), KEY_MINIMUM)

        if not key_count == self.correct_key_count:
            raise RuntimeError("Key count must be within {}-{}".format(KEY_MINIMUM, KEY_MAXIMUM))

        self.key_names = key_names
        self.throttle_limit = throttle_limit
        self.throttler = throttler
        self.connector = connector
        self.timeout = timeout
        self.cache_max_size = cache_max_size
        self.stats_max_size = stats_max_size

        self.http = None  # set in method login()
        self._ready = asyncio.Event()
        self.correct_tags = correct_tags

        # cache
        self._players = {}
        self._clans = {}
        self._wars = {}

    async def login(self, email: str, password: str) -> None:
        self.http = HTTPClient(
            client=self,
            email=email,
            password=password,
            key_names=self.key_names,
            loop=self.loop,
            key_count=self.correct_key_count,
            throttle_limit=self.throttle_limit,
            throttler=self.throttler,
            connector=self.connector,
            timeout=self.timeout,
            cache_max_size=self.cache_max_size,
        )
        await self.http.get_keys()
        await self._ready.wait()
        self._ready.clear()
        LOG.debug("HTTP connection created. Client is ready for use.")
