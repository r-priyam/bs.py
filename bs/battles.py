from datetime import datetime
from typing import List, Optional, Literal, Union

from .abc import BaseBattle, BasePlayer, BaseModel
from .utils import from_timestamp


__all__ = (
    "BattleLogEntry",
    "Brawler",
    "BattlePlayer",
    "SoloBattle",
    "DuoBattle",
    "TeamBattle"
)


class Brawler(BaseModel):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._power_level = data.get("power")
        self._trophies = data.get("trophies")

    @property
    def power_level(self) -> Optional[int]:
        return self._power_level

    @property
    def trophies(self) -> Optional[int]:
        return self._trophies


class BattlePlayer(BasePlayer):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._brawler_data = data.get("brawler")

    @property
    def brawler(self) -> Optional[Brawler]:
        return Brawler(data=self._brawler_data) if self._brawler_data else None


class SoloBattle(BaseBattle):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._rank = data.get("rank")
        self._players_data = data.get("players")

    @property
    def rank(self) -> Optional[int]:
        return self._rank

    @property
    def players(self) -> Optional[List[BattlePlayer]]:
        return [BattlePlayer(data=i) for i in self._players_data] if self._players_data else None


class DuoBattle(BaseBattle):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._rank = data.get("rank")
        self._teams_data = data.get("teams")
        self._teams = []
        if self._teams_data is not None:
            for team in self._teams_data:
                _players = []
                for player in team:
                    _players.append(BattlePlayer(data=player))
                self._teams.append(_players)

    @property
    def rank(self) -> Optional[int]:
        return self._rank

    @property
    def teams(self) -> List[List[BattlePlayer]]:
        return self._teams


class TeamBattle(BaseBattle):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._raw_data = data
        self._teams_data = data.get("teams")
        self._teams = []
        if self._teams_data is not None:
            for team in self._teams_data:
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


class BattleLogEntry:
    __slots__ = (
        "_time",
        "_battle_data",
        "_event"
    )

    def __init__(self, *, data: dict):
        self._time = data.get("battleTime")
        self._event = data.get("event")
        self._battle_data = data.get("battle")

    @staticmethod
    def _get_battle_mode(battle_data: dict):
        if battle_data.get("mode") == "soloShowdown":
            return SoloBattle(data=battle_data)
        if battle_data.get("mode") == "duoShowdown":
            return DuoBattle(data=battle_data)
        return TeamBattle(data=battle_data)

    @property
    def event_id(self) -> Optional[int]:
        return self._event.get("id") if self._event else None

    @property
    def map(self) -> Optional[str]:
        return self._event.get("map") if self._event else None

    @property
    def time(self) -> Optional[datetime]:
        return from_timestamp(self._time) if self._time else None

    @property
    def battle(self) -> Optional[Union[SoloBattle, DuoBattle, TeamBattle]]:
        return self._get_battle_mode(battle_data=self._battle_data) if self._battle_data else None
