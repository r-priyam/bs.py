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

    def __init__(self, *, data, client, **_):
        self._client = client
        self._response_retry = data.get("_response_retry")

        self.tag = data.get("tag")
        self.name = data.get("name")
