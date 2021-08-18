from bs.abc import BaseClub


class Club(BaseClub):
    def __init__(self, *, data: dict) -> None:
        super().__init__(data=data)
        self.data = data

    @property
    def description(self) -> str:
        return self.data.get('description')

    @property
    def type(self) -> str:
        return self.data.get('type')

    @property
    def required_trophies(self) -> int:
        return self.data.get('requiredTrophies')

    @property
    def trophies(self) -> int:
        return self.data.get('trophies')

    # TODO: members attribute (will return List[ClubMember] )

