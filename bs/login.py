from .client import Client


def login(email: str, password: str, **kwargs) -> Client:
    instance = Client(**kwargs)
    instance.loop.run_until_complete(instance.login(email, password))
    return instance
