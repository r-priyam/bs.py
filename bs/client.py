import asyncio
import logging
from typing import Type, Union, List

from .abc import BaseBrawler
from .battles import BattleLogEntry
from .clubs import Club, ClubMember
from .http import BasicThrottler, BatchThrottler, HTTPClient
from .players import Player
from .utils import correct_tag

KEY_MINIMUM, KEY_MAXIMUM = 1, 10
LOG = logging.getLogger(__name__)

__all__ = "Client"


class Client:
    """
    Client connection to interact with the api.

    Parameters
    ----------
    key_count : int
        The amount of keys to use for this client. Maximum of 10.
        Defaults to 1.
    key_names : str
        Default name for keys created to use for this client.
        All keys created or to be used with this client must
        have this name.
        Defaults to "Created with coc.py Client".
    throttle_limit : int
        The number of requests per token per second to send to the API.
        Once hitting this limit, the library will automatically throttle
        your requests.

        .. note::
            Setting this value too high may result in the API rate-limiting
            your requests. This means you cannot request for ~30-60 seconds.

        .. warning::
            Setting this value too high may result in your requests being
            deemed "API Abuse", potentially resulting in an IP ban.

        Defaults to 10 requests per token, per second.

    loop : :class:`asyncio.AbstractEventLoop`, optional
        The :class:`asyncio.AbstractEventLoop` to use for HTTP requests.
        An :func:`asyncio.get_event_loop()` will be used if ``None`` is passed

    correct_tags : :class:`bool`
        Whether the client should correct tags before requesting them from the API.
        This process involves stripping tags of whitespace and adding a `#` prefix if not present.
        Defaults to ``True``.

    connector : :class:`aiohttp.BaseConnector`
        The aiohttp connector to use. By default this is ``None``.

    timeout: :class:`float`
        The number of seconds before timing out with an API query. Defaults to 30.

    cache_max_size: :class:`int`
        The max size of the internal cache layer. Defaults to 10,000. Set this to ``None`` to remove any cache layer.

    """

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

        if key_count != self.correct_key_count:
            raise RuntimeError(
                f"Key count must be within {KEY_MINIMUM}-{KEY_MAXIMUM}"
            )

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

    def close(self) -> None:
        """Closes the HTTP connection."""
        if self.http:
            LOG.info("Brawl Stars client logging out...")
            self.dispatch("on_client_close")
            self.loop.run_until_complete(self.http.close())
            self.loop.close()

    def dispatch(self, event_name: str, *args, **kwargs) -> None:
        LOG.debug("Dispatching %s event", event_name)

        try:
            fctn = getattr(self, event_name)
        except AttributeError:
            return

        if asyncio.iscoroutinefunction(fctn):
            self.loop.create_task(fctn(*args, **kwargs))
        else:
            fctn(*args, **kwargs)

    async def reset_keys(self, number_of_keys: int = None) -> None:
        self._ready.clear()
        if self.http and self.http._keys:
            num = number_of_keys or len(self.http._keys)
            keys = self.http._keys
            for i in range(num):
                await self.http.reset_key(keys[i])
            self._ready.set()

    async def get_player(self, player_tag: str) -> Player:
        """
        |coro|

        Fetches the player's info.

        Parameters
        ----------
        player_tag: str
            The tag of the player to fetch the player's info.

        Returns
        -------
        :class:`Player`
            A player object with all it's attributes.

        Raises
        ------



        """
        if self.correct_tags:
            player_tag = correct_tag(player_tag)

        if self.http:
            data = await self.http.get_player(player_tag)
            return Player(data=data)

    async def get_player_battle_log(
        self, player_tag: str
    ) -> List[BattleLogEntry]:
        """
        |coro|

        Fetches battle logs of a player.

        Parameters
        ----------
        player_tag: str
            The tag of the player to fetch the battle log.

        Returns
        -------
        :class:`List[BattleLogEntry]`
            List of :class:`BattleLogEntry` which contains 30 recent battles.

            .. note::
                Battles may take upto 30 minutes to appear in logs.

        """
        if self.correct_tags:
            player_tag = correct_tag(player_tag)

        if self.http:
            data = await self.http.get_player_battle_log(player_tag)
            data_list = data.get("items")
            return [BattleLogEntry(data=i) for i in data_list]

    async def get_club(self, club_tag: str) -> Club:
        if self.correct_tags:
            club_tag = correct_tag(club_tag)

        if self.http:
            data = await self.http.get_club(club_tag)
            return Club(data=data)

    async def get_club_members(
        self, club_tag: str, limit: int = None
    ) -> List[ClubMember]:
        if self.correct_tags:
            club_tag = correct_tag(club_tag)

        if self.http:
            data = await self.http.get_club_members(club_tag, limit=limit)
            data_list = data.get("items")
            return [ClubMember(data=i) for i in data_list]

    async def get_brawlers(self, limit: int = None) -> List[BaseBrawler]:
        if self.http:
            data = await self.http.get_brawlers(limit=limit)
            data_list = data.get("items")
            return [BaseBrawler(data=i) for i in data_list]

    async def get_brawler(self, brawler_id: int) -> BaseBrawler:
        if self.http:
            data = await self.http.get_brawler(brawler_id)
            return BaseBrawler(data=data)
