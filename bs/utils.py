import inspect
import re

from collections import deque
from datetime import datetime
from functools import wraps
from operator import attrgetter
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

TAG_VALIDATOR = re.compile("^#?[PYLQGRJCUV0289]+$")

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


def find(predicate: Callable[[T], Any], iterable: Iterable[T]) -> Optional[T]:
    for element in iterable:
        if predicate(element):
            return element
    return None


def get(iterable: Iterable[T], **attrs: Any) -> Optional[T]:
    converted = [(attrgetter(attr), value) for attr, value in attrs.items()]
    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            return elem
    return None


def from_timestamp(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y%m%dT%H%M%S.000Z")


def is_valid_tag(tag: str) -> bool:
    return bool(TAG_VALIDATOR.match(correct_tag(tag)))


def correct_tag(tag: str, prefix: str = "#") -> str:
    return tag and prefix + re.sub(r"[^A-Z0-9]+", "", tag.upper()).replace("O", "0")


def corrected_tag() -> Callable[[Callable[..., T]], Callable[..., T]]:
    def deco(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self = args[0]

            if not self.correct_tags:
                return func(*args, **kwargs)

            args = list(args)
            args[1] = correct_tag(args[1])
            return func(*tuple(args), **kwargs)

        return wrapper

    return deco


def maybe_sort(
    seq: Iterable[T],
    sort: bool,
    itr: bool = False,
    key: Callable[[str], Any] = attrgetter("order"),
) -> Union[List[T], Iterable[T]]:
    return (
        (list, iter)[itr](n for n in sorted(seq, key=key))
        if sort
        else (list, iter)[itr](n for n in seq)
    )


def item(
    _object,
    *,
    index: bool = False,
    index_type: Union[int, str] = 0,
    attribute: str = None,
    index_before_attribute: bool = True
):
    attr_get = attrgetter(attribute or "")
    if not (index or index_type or attribute):
        return _object
    if (index or index_type) and not attribute:
        return _object[index_type]
    if not index and not index_type:
        return attr_get(_object)
    if index_before_attribute:
        return attr_get(_object[index_type])
    return attr_get(_object)[index_type]


def custom_isinstance(obj, module, name):
    for cls in inspect.getmro(type(obj)):
        try:
            if cls.__module__ == module and cls.__name__ == name:
                return True
        except Exception:
            pass
    return False


async def maybe_coroutine(function_, *args, **kwargs):
    value = function_(*args, **kwargs)
    if inspect.isawaitable(value):
        return await value

    return value


class _CachedProperty(Generic[T, T_co]):
    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self.name = name
        self.function = function
        self.__doc__ = getattr(function, "__doc__")

    def __get__(self, instance: T, owner: Type[T]) -> T_co:
        try:
            return getattr(instance, self.name)
        except AttributeError:
            result = self.function(instance)
            setattr(instance, self.name, result)
            return result


def cached_property(
    name: str,
) -> Callable[[Callable[[T], T_co]], _CachedProperty[T, T_co]]:
    def deco(func: Callable[[T], T_co]) -> _CachedProperty[T, T_co]:
        return _CachedProperty(name, func)

    return deco


class LRU(dict):
    __slots__ = ("__keys", "max_size")

    def __init__(self, max_size):
        self.max_size = max_size
        self.__keys = deque()
        super().__init__()

    def __verify_max_size(self):
        while len(self) > self.max_size:
            del self[self.__keys.popleft()]

    def __setitem__(self, key, value):
        self.__keys.append(key)
        super().__setitem__(key, value)
        self.__verify_max_size()

    def __getitem__(self, key):
        self.__verify_max_size()
        return super().__getitem__(key)

    def __contains__(self, key):
        self.__verify_max_size()
        return super().__contains__(key)
