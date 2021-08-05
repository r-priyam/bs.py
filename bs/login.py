import typing

from .client import Client


def login(
        email: str, password: str, client: typing.Type[typing.Optional[Client]] = Client, **kwargs
) -> typing.Optional[Client]:
    instance = client(**kwargs)
    instance.loop.run_until_complete(instance.login(email, password))
    return instance
