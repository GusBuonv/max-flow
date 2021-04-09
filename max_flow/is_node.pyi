from typing import TypeVar
from util.data_structures.BSTNodeI import BSTNodeI
from typing_extensions import TypeGuard
from max_flow.PathTree import PathTree
from util.types import Nullable

T = TypeVar('T', bound=PathTree)
def is_node(val: Nullable[T]) -> TypeGuard[T]: ...
