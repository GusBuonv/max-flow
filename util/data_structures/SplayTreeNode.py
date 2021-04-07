from typing import TypeVar, Generic, Optional, Tuple
from util.data_structures.BSTNode import BSTNode
from util.data_structures.BSTNodeI import BSTNodeI
from util.data_structures.is_node import is_node
from util.constants import NULL, RIGHT
from util.types import Nullable

T = TypeVar('T')
S = TypeVar('S', bound='BSTNodeI')

class SplayTreeNode(BSTNode, Generic[T]):
	def __init__(self, value: T) -> None:
		super().__init__()
		self.value = value

	@property
	def side(self): return self.is_on(RIGHT)

	def rotate(self: S, lookAhead: Optional[Tuple[Nullable[S], bool]] = None) -> Optional[Tuple[Nullable[S], bool]]:
		if lookAhead:
			(parent, side) = lookAhead
		else:
			parent = self.parent
			side = self is parent.right

		if is_node(parent):
			side_0 = not side
			save_child = self.give(side_0)
			parent.swap(side, save_child)
			grand_parent = parent.parent
			grand_side = parent is grand_parent.right
			grand_parent.swap(grand_side, self)
			self.swap(side_0, parent)
			return (grand_parent, grand_side)
