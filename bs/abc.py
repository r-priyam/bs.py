__all__ = ("BasePlayer", "BaseClub")


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
