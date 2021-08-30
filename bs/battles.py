from datetime import datetime
from typing import List, Optional, Literal

from .abc import Event, BaseBattle, BasePlayer, BaseModel
from .utils import from_timestamp


class BattleLog:
    __slots__ = (
        "_time",
        "_battle",
        "_event"
    )

    def __init__(self, *, data: dict):
        self._time = data.get("battleTime")
        self._event = data.get("event")
        self._battle = data.get("battle")  # TODO: Create a Battle object

    async def get_battle_mode(self, *, battle_data: dict):
        if battle_data:
            return None

    @property
    def time(self) -> datetime:
        return from_timestamp(self._time)

    @property
    def event(self) -> Event:
        return Event(data=self._event)

    @property
    def battle(self):
        return None


class Brawler(BaseModel):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._power_level = data.get("power")
        self._trophies = data.get("trophies")

    @property
    def power_level(self) -> int:
        return self._power_level

    @property
    def trophies(self) -> int:
        return self._trophies


class BattlePlayer(BasePlayer):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._brawler_data = data.get("brawler")

    @property
    def brawler(self) -> Brawler:
        return Brawler(data=self._brawler_data)


class SoloBattle(BaseBattle):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._rank = data.get("rank")
        self._players_data = data.get("players")

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def players(self) -> List[BattlePlayer]:
        return [BattlePlayer(data=i) for i in self._players_data]


class DuoBattle(BaseBattle):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._rank = data.get("rank")
        self._teams = []
        for team in data.get("teams"):
            _players = []
            for player in team:
                _players.append(BattlePlayer(data=player))
            self._teams.append(_players)

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def teams(self) -> List[List[BattlePlayer]]:
        return self._teams


class TeamBattle(BaseBattle):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._raw_data = data
        self._teams = []
        for team in self._raw_data.get("teams"):
            _players = []
            for player in team:
                _players.append(BattlePlayer(data=player))
            self._teams.append(_players)

    @property
    def result(self) -> Optional[Literal["victory", "defeat", "draw"]]:
        return self._raw_data.get("result")

    @property
    def star_player(self) -> BattlePlayer:
        return BattlePlayer(data=self._raw_data.get("starPlayer"))

    @property
    def duration(self) -> Optional[int]:
        """Duration of the battle (in seconds)"""
        return self._raw_data.get("duration")

    @property
    def teams(self) -> List[List[BattlePlayer]]:
        return self._teams
