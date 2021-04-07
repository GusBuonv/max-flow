from typing import TypeVar, Union
from .Null import Null

T = TypeVar('T')

Nullable = Union[T, Null]
