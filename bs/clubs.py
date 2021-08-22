import typing

from bs.abc import BaseClub, BasePlayer

__all__ = (
    "ClubMember",
    "Club"
)

class ClubMember(BasePlayer):
    """Represents a member of a club."""
    def __init__(self, *, data: dict) -> None:
        super().__init__(data=data)
        self._data = data

    @property
    def name_color(self) -> str:
        return self._data.get('nameColor')

    @property
    def role(self) -> typing.Literal["member", "senior", "vicePresident", "president"]:
        return self._data.get('role')

    @property
    def trophies(self) -> int:
        return self._data.get('trophies')


class Club(BaseClub):

    def __init__(self, *, data: dict) -> None:
        super().__init__(data=data)
        self._data = data

    @property
    def description(self) -> str:
        return self._data.get('description')

    @property
    def type(self) -> typing.Literal["open", "inviteOnly", "closed"]:
        return self._data.get('type')

    @property
    def required_trophies(self) -> int:
        return self._data.get('requiredTrophies')

    @property
    def trophies(self) -> int:
        return self._data.get('trophies')

    @property
    def members(self) -> typing.List[ClubMember]:
        member_list = [ClubMember(data=i) for i in self._data.get("members")]
        return member_list

    @property
    def member_count(self) -> int:
        return len(self.members)
