from ..types import Nullable, TypeVar
from ..constants import NULL
from .BSTNodeI import BSTNodeI

T = TypeVar('T', bound=BSTNodeI)

def is_node(val: Nullable[T]) -> bool:
	return val is not NULL
