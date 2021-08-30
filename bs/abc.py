__all__ = (
    "BasePlayer",
    "BaseClub",
    "BaseModel",
    "BaseBrawler",
    "BaseBattle",
    "StarPower",
    "Gadget"
)

from typing import List, Literal, Optional


class BasePlayer:
    __slots__ = ("tag", "name", "_client", "_response_retry")

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s tag=%s name='%s'>" % (
            self.__class__.__name__,
            self.tag,
            self.name,
        )

    def __eq__(self, other):
        return isinstance(other, BasePlayer) and self.tag == other.tag

    def __init__(self, *, data: dict, client=None, **_):
        self._client = client
        self._response_retry = data.get("_response_retry")

        self.tag: Optional[str] = data.get("tag")
        self.name: Optional[str] = data.get("name")


class BaseClub:
    __slots__ = ("_tag", "_name")

    def __eq__(self, other):
        return isinstance(other, BaseClub) and self.tag == other.tag

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s tag=%s name='%s'>" % (
            self.__class__.__name__,
            self.tag,
            self.name,
        )

    def __init__(self, *, data: dict):
        self._name: Optional[str] = data.get("name")
        self._tag: Optional[str] = data.get("tag")

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def tag(self) -> Optional[str]:
        return self._tag


class BaseModel:
    __slots__ = ("_id", "_name")

    def __init__(self, *, data: dict):
        self._id: Optional[int] = data.get("id")
        self._name: Optional[str] = data.get("name")

    def __eq__(self, other):
        return isinstance(self, other) and self.id == other.id and self.name == other.name

    def __repr__(self):
        return "<%s name='%s' id=%s>" % (
            self.__class__.__name__,
            self.name,
            self.id,
        )

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> Optional[str]:
        return self._name


class StarPower(BaseModel):
    def __init__(self, *, data: dict):
        super().__init__(data=data)


class Gadget(BaseModel):
    def __init__(self, *, data: dict):
        super().__init__(data=data)


class BaseBrawler(BaseModel):
    def __init__(self, *, data: dict):
        super().__init__(data=data)
        self._star_powers = data.get("starPowers")
        self._gadgets = data.get("gadgets")

    @property
    def star_powers(self) -> Optional[List[StarPower]]:
        return [StarPower(data=i) for i in self._star_powers] if self._star_powers else None

    @property
    def gadgets(self) -> Optional[List[Gadget]]:
        return [Gadget(data=i) for i in self._gadgets] if self._gadgets else None


class BaseBattle:
    __slots__ = ("_mode", "_type", "_trophy_change")

    def __repr__(self):
        return "<%s type='%s', mode='%s', trophy_changed=%s>" % (
            self.__class__.__name__,
            self.battle_type,
            self.mode,
            self.trophy_change,
        )

    def __init__(self, *, data: dict):
        self._mode = data.get("mode")
        self._type = data.get("type")
        self._trophy_change = data.get("trophyChange")

    @property
    def mode(self) -> Optional[str]:
        return self._mode

    @property
    def trophy_change(self) -> Optional[int]:
        return self._trophy_change
    
    @property
    def battle_type(self) -> Optional[Literal["ranked", "friendly", "challenge"]]:
        return self._type
