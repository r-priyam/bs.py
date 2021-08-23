import asyncio
import logging
import re
from collections import deque
from datetime import datetime
from itertools import cycle
from time import perf_counter, process_time
from urllib.parse import urlencode

import aiohttp

from .errors import (
    Forbidden,
    GatewayError,
    HTTPException,
    InvalidArgument,
    InvalidCredentials,
    Maintenance,
    NotFound,
)
from .utils import LRU

LOG = logging.getLogger(__name__)
KEY_MINIMUM, KEY_MAXIMUM = 1, 10
stats_url_matcher = re.compile(r"%23[\da-zA-Z]+|\d{8,}|global")


async def json_or_text(response):
    try:
        ret = await response.json()
    except aiohttp.ContentTypeError:
        ret = await response.text(encoding="utf-8")

    return ret


class BasicThrottler:
    __slots__ = (
        "sleep_time",
        "last_run",
        "lock",
    )

    def __init__(self, sleep_time):
        self.sleep_time = sleep_time
        self.last_run = None
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            last_run = self.last_run
            if last_run:
                difference = process_time() - last_run
                need_to_sleep = self.sleep_time - difference
                if need_to_sleep > 0:
                    LOG.debug("Request throttled. Sleeping for %s", need_to_sleep)
                    await asyncio.sleep(need_to_sleep)

            self.last_run = process_time()
            return self

    async def __aexit__(self, exception_type, exception, traceback):
        pass


class BatchThrottler:
    __slots__ = ("rate_limit", "per", "retry_interval", "_task_logs")

    def __init__(self, rate_limit, per=1.0, retry_interval=0.001):
        self.rate_limit = rate_limit
        self.per = per
        self.retry_interval = retry_interval

        self._task_logs = deque()

    async def __aenter__(self):
        while True:
            now = process_time()

            while self._task_logs:
                if now - self._task_logs[0] > self.per:
                    self._task_logs.popleft()
                else:
                    break

            if len(self._task_logs) < self.rate_limit:
                break

            retry_interval = self.retry_interval
            LOG.debug("Request throttled. Sleeping for %s seconds.", retry_interval)
            await asyncio.sleep(retry_interval)

        self._task_logs.append(process_time())

        return self

    async def __aexit__(self, exception_type, exception, traceback):
        pass


class Route:
    BASE = "https://api.brawlstars.com/v1"
    API_PAGE_BASE = "https://developer.brawlstars.com/api"

    def __init__(self, method, path: str, api_page: bool = False, **kwargs):
        if "#" in path:
            path = path.replace("#", "%23")

        self.method = method
        self.path = path
        url = self.API_PAGE_BASE + self.path if api_page else self.BASE + self.path

        if kwargs:
            self.url = "{}?{}".format(
                url, urlencode({k: v for k, v in kwargs.items() if v is not None})
            )
        else:
            self.url = url

    @property
    def stats_key(self):
        return stats_url_matcher.sub("{}", self.path)


class HTTPClient:
    def __init__(
        self,
        client,
        loop,
        email,
        password,
        key_names,
        key_count,
        throttle_limit,
        throttler=BasicThrottler,
        connector=None,
        timeout=30.0,
        cache_max_size=10000,
    ):
        self.client = client
        self.loop = loop
        self.email = email
        self.password = password
        self.key_names = key_names
        self.key_count = key_count
        self.throttle_limit = throttle_limit

        per_second = key_count * throttle_limit

        self.__lock = asyncio.Semaphore(per_second)
        self.cache = cache_max_size and LRU(cache_max_size)

        if issubclass(throttler, BasicThrottler):
            self.__throttle = throttler(1 / per_second)
        elif issubclass(throttler, BatchThrottler):
            self.__throttle = throttler(per_second)
        else:
            raise TypeError(
                "throttler must be either BasicThrottler or BatchThrottler."
            )

        self.__session = aiohttp.ClientSession(
            connector=connector, timeout=aiohttp.ClientTimeout(total=timeout)
        )

        self._keys = None
        self.keys = None

    def _cache_remove(self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass

    async def close(self):
        if self.__session:
            await self.__session.close()

    # noinspection PyUnboundLocalVariable
    async def request(self, route, **kwargs):
        method = route.method
        url = route.url
        api_request = kwargs.pop("api_request", False)

        if not api_request:
            key = next(self.keys)

            headers = {
                "Accept": "application/json",
                "authorization": "Bearer {}".format(key),
            }
            kwargs["headers"] = headers

        if "json" in kwargs:
            kwargs["headers"]["Content-Type"] = "application/json"

        cache_control_key = route.url
        cache = self.cache
        if cache is not None:
            try:
                return cache[cache_control_key]
            except KeyError:
                pass

        for tries in range(5):
            try:
                async with self.__lock, self.__throttle:
                    start = perf_counter()
                    async with self.__session.request(
                        method, url, **kwargs
                    ) as response:

                        _perf_counter = (perf_counter() - start) * 1000
                        log_info = {
                            "method": method,
                            "url": url,
                            "perf_counter": _perf_counter,
                            "status": response.status,
                        }

                        LOG.debug("API HTTP Request: %s", str(log_info))
                        data = await json_or_text(response)

                        try:
                            delta = int(
                                response.headers["Cache-Control"].strip("max-age=")
                            )
                            data["_response_retry"] = delta
                            if cache is not None:
                                self.cache[cache_control_key] = data
                                LOG.debug(
                                    "Cache-Control max age: %s seconds, key: %s",
                                    delta,
                                    cache_control_key,
                                )
                                self.loop.call_later(
                                    delta, self._cache_remove, cache_control_key
                                )

                        except (KeyError, AttributeError, ValueError):
                            if isinstance(data, dict):
                                data["_response_retry"] = 0

                        if 200 <= response.status < 300:
                            LOG.debug("%s has received %s", url, data)
                            return data

                        if response.status == 400:
                            raise InvalidArgument(response, data)

                        if response.status == 403:
                            if (
                                data.get("reason") in ["accessDenied.invalidIp"]
                                and not api_request
                            ):
                                await self.reset_key(key)
                                LOG.info("Reset Brawl Stars key")
                                return await self.request(route, **kwargs)

                            raise Forbidden(response, data)

                        if response.status == 404:
                            raise NotFound(response, data)
                        if response.status == 429:
                            LOG.error(
                                "We have been rate-limited by the API. "
                                "Reconsider the number of requests you are allowing per second."
                            )
                            raise HTTPException(response, data)

                        if response.status == 503:
                            if isinstance(data, str):
                                text = re.compile(r"<[^>]+>").sub(data, "")
                                raise Maintenance(response, text)

                            raise Maintenance(response, data)

                        if response.status in (500, 502, 504):
                            await asyncio.sleep(tries * 2 + 1)
                            continue

            except asyncio.TimeoutError:
                if tries > 3:
                    raise GatewayError("The API timed out waiting for the request.")

                await asyncio.sleep(tries * 2 + 1)
                continue
            raise

        else:
            if response.status in (500, 502, 504):
                if isinstance(data, str):
                    text = re.compile(r"<[^>]+>").sub(data, "")
                    raise GatewayError(response, text)

                raise GatewayError(response, data)

            raise HTTPException(response, data)

    # players

    def get_player_battle_log(self, tag):
        return self.request(Route("GET", f"/players/{tag}/battlelog"))

    def get_player(self, tag):
        return self.request(Route("GET", f"/players/{tag}"))

    # clubs

    def get_club_members(self, tag, **kwargs):
        return self.request(Route("GET", f"/clubs/{tag}/members", **kwargs))

    def get_club(self, tag):
        return self.request(Route("GET", f"/clubs/{tag}"))

    # rankings

    # brawlers

    def get_brawlers(self, **kwargs):
        return self.request(Route("GET", "/brawlers", **kwargs))

    def get_brawler(self, _id):
        return self.request(Route("GET", f"/brawlers/{_id}"))

    # events

    def get_event_rotation(self):
        return self.request(Route("GET", "/events/rotation"))

    # key updating management

    async def get_ip(self):
        url = "https://api.ipify.org/"
        async with self.__session.request("GET", url) as response:
            LOG.debug("%s (%s) has returned %s", url, "GET", response.status)
            ip_ = await response.text()
            LOG.debug("%s has received %s", url, ip_)
        return ip_

    @staticmethod
    def create_cookies(response_dict, session):
        try:
            return (
                f"game-api-url={response_dict['swaggerUrl']}; session={session}; "
                f"game-api-token={response_dict['temporaryAPIToken']}"
            )
        except KeyError:
            return None

    async def get_keys(self):
        response_dict, session = await self.login_to_site(self.email, self.password)
        cookies = self.create_cookies(response_dict, session)

        headers = {
            "cookies": cookies,
            "content-type": "application/json",
        }

        ip = await self.get_ip()
        current_keys = (await self.find_site_keys(headers))["keys"]

        self._keys = [
            key["key"]
            for key in current_keys
            if key["name"] == self.key_names and ip in key["cidrRanges"]
        ]

        required_key_count = self.key_count
        current_key_count = len(current_keys)

        if required_key_count > len(self._keys):
            for key in (
                k
                for k in current_keys
                if k["name"] == self.key_names and ip not in k["cidrRanges"]
            ):
                try:
                    await self.delete_key(cookies, key["id"])
                except (InvalidArgument, NotFound):
                    continue
                else:
                    new = await self.create_key(cookies)
                    self._keys.append(new)
                    self.client.dispatch("on_key_reset", new)

            make_keys = required_key_count - len(self._keys)
            for _ in range(make_keys):
                if current_key_count >= KEY_MAXIMUM:
                    break

                new = await self.create_key(cookies)
                self._keys.append(new)
                self.client.dispatch("on_key_reset", new)
                current_key_count += 1

        if current_key_count == KEY_MAXIMUM and len(self._keys) < required_key_count:
            LOG.critical(
                "%s keys were requested to be used, but a maximum of %s could be "
                "found/made on the developer site, as it has a maximum of 10 keys per account. "
                "Please delete some keys or lower your `key_count` level."
                "I will use %s keys for the life of this client.",
                required_key_count,
                current_key_count,
                current_key_count,
            )

        if not self._keys:
            await self.close()
            raise RuntimeError(
                "There are {} API keys already created and none match a key_name of '{}'."
                "Please specify a key_name kwarg, or go to 'https://developer.brawlstars.com' to delete "
                "unused keys.".format(current_key_count, self.key_names)
            )

        self.keys = cycle(self._keys)
        self.client._ready.set()

    async def reset_key(self, key):
        response_dict, session = await self.login_to_site(self.email, self.password)
        cookies = self.create_cookies(response_dict, session)

        if cookies is None:
            return

        headers = {
            "cookies": cookies,
            "content-type": "application/json",
        }

        existing_keys_dict = await self.find_site_keys(headers)
        try:
            existing_keys = existing_keys_dict["keys"]
        except (TypeError, KeyError):
            return

        key_id = [t["id"] for t in existing_keys if t["key"] == key]

        try:
            await self.delete_key(cookies, key_id)
        except (InvalidArgument, NotFound):
            return

        new_key = await self.create_key(cookies)
        keys = self._keys
        key_index = keys.index(key)
        self._keys = keys[key_index:] + keys[:key_index]

        self._keys[0] = new_key
        self.keys = cycle(self._keys)
        self.client.dispatch("key_reset", new_key)

    async def login_to_site(self, email, password):
        login_data = {"email": email, "password": password}
        headers = {"content-type": "application/json"}
        async with self.__session.post(
            "https://developer.brawlstars.com/api/login",
            json=login_data,
            headers=headers,
        ) as sess:
            response_dict = await sess.json()
            LOG.debug(
                "%s has received %s",
                "https://developer.brawlstars.com/api/login",
                response_dict,
            )
            if sess.status == 403:
                await self.close()
                raise InvalidCredentials(sess, response_dict)

            session = sess.cookies.get("session").value

        return response_dict, session

    async def find_site_keys(self, headers):
        url = "https://developer.brawlstars.com/api/apikey/list"
        async with self.__session.post(url, json={}, headers=headers) as sess:
            existing_keys_dict = await sess.json()
            LOG.debug("%s has received %s", url, existing_keys_dict)

        return existing_keys_dict

    async def create_key(self, cookies):
        headers = {"cookie": cookies, "content-type": "application/json"}

        data = {
            "name": self.key_names,
            "description": "Created on {}".format(datetime.now().strftime("%c")),
            "cidrRanges": [await self.get_ip()],
            "scopes": None,  # Well API is being PITA if set to any value.
        }

        response = await self.request(
            Route("POST", "/apikey/create", api_page=True),
            json=data,
            headers=headers,
            api_request=True,
        )
        return response["key"]["key"]

    def delete_key(self, cookies, key_id):
        headers = {"cookie": cookies, "content-type": "application/json"}

        data = {"id": key_id}

        return self.request(
            Route("POST", "/apikey/revoke", api_page=True),
            json=data,
            headers=headers,
            api_request=True,
        )
