from datetime import datetime

from .abc import Event
from .utils import from_timestamp


class BattleLog:
    def __init__(self, *, data: dict):
        self._time = data.get("battleTime")
        self._event = data.get("event")
        self._battle = data.get("battle")  # TODO: Create a Battle object

    @property
    def time(self) -> datetime:
        return from_timestamp(self._time)

    @property
    def event(self) -> Event:
        return Event(data=self._event)
