from typing import Optional

__all__ = ("ClubPlayer", "Player")


class ClubPlayer:
    __slots__ = ("club_tag", "club_name")

    def __init__(self, *, data) -> None:
        _data_get = data.get("club")
        self.club_name: str = _data_get.get("name")
        self.club_tag: str = _data_get.get("tag")


class Player(ClubPlayer):
    __slots__ = (
        "tag",
        "name",
        "name_color",
        "name_colour",
        "trophies",
        "best_trophies",
        "best_power_play_points",
        "exp_level",
        "exp_points",
        "qualified_for_championship",
        "trio_victories",
        "duo_victories",
        "solo_victories",
        "best_robo_rumble_time",
        "best_big_brawler_time",
    )

    def __init__(self, *, data) -> None:
        super().__init__(data=data)
        self._from_data(data)

    def _from_data(self, data: dict) -> None:
        data_get = data.get
        self.tag: Optional[str] = data_get("tag")
        self.name: Optional[str] = data_get("name")
        self.name_color: Optional[str] = data_get("nameColor")
        self.name_colour = self.name_color
        self.trophies: Optional[int] = data_get("trophies")
        self.best_trophies: Optional[int] = data_get("highestTrophies")
        self.best_power_play_points: Optional[int] = data_get("highestPowerPlayPoints")
        self.exp_level: Optional[int] = data_get("expLevel")
        self.exp_points: Optional[int] = data_get("expPoints")
        self.qualified_for_championship: Optional[bool] = data_get("isQualifiedFromChampionshipChallenge")
        self.trio_victories: Optional[int] = data_get("3vs3Victories")
        self.duo_victories: Optional[int] = data_get("duoVictories")
        self.solo_victories: Optional[int] = data_get("soloVictories")
        self.best_robo_rumble_time: Optional[int] = data_get("bestRoboRumbleTime")
        self.best_big_brawler_time: Optional[int] = data_get("bestTimeAsBigBrawler")
