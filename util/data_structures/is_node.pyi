from typing import TypeVar
from util.data_structures.BSTNodeI import BSTNodeI
from typing_extensions import TypeGuard
from ..types import Nullable
from .BSTNodeI import BSTNodeI

T = TypeVar('T', bound=BSTNodeI)
def is_node(val: Nullable[T]) -> TypeGuard[T]: ...
