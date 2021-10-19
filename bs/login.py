from .client import Client


def login(email: str, password: str, **kwargs) -> Client:
    """
    This function makes logging in easy with email and password.

    Parameters
    ----------
    email: str
        Your email of https://developer.brawlstars.com.
    password: str
        Your password of https://developer.brawlstars.com.

        .. note::

            Your email and password is used to update the keys
            when your IP changes.

    **kwargs
        Any kwargs you wish to pass into the :class:`Client` object.

    Returns
    -------
    :class:`Client`
        :class:`Client` object to interact with the API

    Raises
    ------
    :class:`InvalidCredentials`
        Wrong email or password provided.

    """
    instance = Client(**kwargs)
    instance.loop.run_until_complete(instance.login(email, password))
    return instance
