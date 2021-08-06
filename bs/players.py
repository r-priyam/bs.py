class ClubPlayer:
    __slots__ = ("club_tag", "club_name")

    def __init__(self, *, data) -> None:
        _data_get = data.get("club")
        self.club_name = _data_get.get("name")
        self.club_tag = _data_get.get("tag")


class Player(ClubPlayer):
    __slots__ = (
        "tag",
        "name",
        "name_color",
        "trophies",
        "best_trophies",
        "best_power_play_points",
        "exp_level",
        "exp_points",
        "qualified_for_championship",
        "trio_victories",
        "duo_victories",
        "solo_victories",
        "best_RoboRumble_time",
        "best_BigBrawler_time",
    )

    def __init__(self, *, data):
        super().__init__(data=data)
        self._from_data(data)

    def _from_data(self, data: dict) -> None:
        data_get = data.get
        self.tag = data_get("tag")
        self.name = data_get("name")
        self.name_color = data_get("nameColor")
        self.trophies = data_get("trophies")
        self.best_trophies = data_get("highestTrophies")
        self.best_power_play_points = data_get("highestPowerPlayPoints")
        self.exp_level = data_get("expLevel")
        self.exp_points = data_get("expPoints")
        self.qualified_for_championship = data_get("isQualifiedFromChampionshipChallenge")
        self.trio_victories = data_get("3vs3Victories")
        self.duo_victories = data_get("duoVictories")
        self.solo_victories = data_get("soloVictories")
        self.best_RoboRumble_time = data_get("bestRoboRumbleTime")
        self.best_BigBrawler_time = data_get("bestTimeAsBigBrawler")
