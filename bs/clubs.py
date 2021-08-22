from typing import List, Literal, Union

from .abc import BaseClub, BasePlayer

__all__ = ("ClubMember", "Club")


class ClubMember(BasePlayer):
    """Represents a member of a club."""

    def __init__(self, *, data: dict) -> None:
        super().__init__(data=data)
        self._data = data

    @property
    def name_color(self) -> Union[str, None]:
        return self._data.get("nameColor")

    @property
    def role(self) -> Literal["member", "senior", "vicePresident", "president", None]:
        return self._data.get("role")

    @property
    def trophies(self) -> Union[int, None]:
        return self._data.get("trophies")


class Club(BaseClub):
    def __init__(self, *, data: dict) -> None:
        super().__init__(data=data)
        self._data = data

    @property
    def description(self) -> Union[str, None]:
        return self._data.get("description")

    @property
    def type(self) -> Literal["open", "inviteOnly", "closed", None]:
        return self._data.get("type")

    @property
    def required_trophies(self) -> Union[int, None]:
        return self._data.get("requiredTrophies")

    @property
    def trophies(self) -> Union[int, None]:
        return self._data.get("trophies")

    @property
    def members(self) -> Union[List[ClubMember], None]:
        if self._data.get("members"):
            return [ClubMember(data=i) for i in self._data["members"]]
        return None

    @property
    def member_count(self) -> int:
        return len(self.members) if self.members else 0
