__all__ = (
    "BasePlayer",
    "BaseClub",
    "BaseModel",
    "BaseBrawler",
    "StarPower",
    "Gadget",
    "Event"
)

from typing import List


class BasePlayer:
    __slots__ = ("tag", "name", "_client", "_response_retry")

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s tag=%s name=%s>" % (
            self.__class__.__name__,
            self.tag,
            self.name,
        )

    def __eq__(self, other):
        return isinstance(other, BasePlayer) and self.tag == other.tag

    def __init__(self, *, data, client=None, **_):
        self._client = client
        self._response_retry = data.get("_response_retry")

        self.tag: str = data.get("tag")
        self.name: str = data.get("name")


class BaseClub:
    __slots__ = ("_tag", "_name")

    def __eq__(self, other):
        return isinstance(other, BaseClub) and self.tag == other.tag

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s tag=%s name=%s>" % (
            self.__class__.__name__,
            self.tag,
            self.name,
        )

    def __init__(self, *, data: dict):
        self._name = data.get("name")
        self._tag = data.get("tag")

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag(self) -> str:
        return self._tag


class BaseModel:
    __slots__ = ("_id", "_name")

    def __init__(self, *, data: dict):
        self._id = data.get("id")
        self._name = data.get("name")

    def __eq__(self, other):
        return isinstance(self, other) and self.id == other.id and self.name == other.name

    def __repr__(self):
        return "<%s name='%s' id=%s>" % (
            self.__class__.__name__,
            self.name,
            self.id,
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
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
    def star_powers(self) -> List[StarPower]:
        return [StarPower(data=i) for i in self._star_powers]

    @property
    def gadgets(self) -> List[Gadget]:
        return [Gadget(data=i) for i in self._gadgets]


class Event:
    __slots__ = (
        "_id",
        "_mode",
        "_map"
    )

    def __init__(self, *, data: dict):
        self._id = data.get("id")
        self._mode = data.get("mode")
        self._map = data.get("map")

    def __repr__(self):
        return "<%s Mode='%s' Map='%s'" % (
            self.__class__.__name__,
            self._mode,
            self._map
        )
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def map(self) -> str:
        return self._map
