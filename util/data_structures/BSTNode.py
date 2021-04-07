from typing import TypeVar, List, Union, cast, Any
from util.Null import Null
from weakref import ref
from util.types import Nullable
from util.constants import NULL, LEFT, RIGHT
from util.data_structures.BSTNodeI import BSTNodeI

T = TypeVar('T')
SI = TypeVar('SI', bound=BSTNodeI)
S = TypeVar('S', bound='BSTNode')

class BSTNode(BSTNodeI):
	def __init__(self) -> None:
		self._parent_ref: Any = ref(NULL)
		self._children: Any = [NULL, NULL]

	@property
	def children(self: S) -> List[Nullable[S]]:
		return self._children

	@property
	def parent(self: S) -> Nullable[S]:
		return self._parent_ref() or NULL

	@property
	def left(self: S) -> Nullable[S]:
		return self.children[LEFT]

	@property
	def right(self: S) -> Nullable[S]:
		return self.children[RIGHT]

	def is_on(self, side: bool) -> bool:
		return self is self.parent.children[side]

	def swap(self: S, side: bool, child: Nullable[S]) -> Nullable[S]:
		child._parent_ref = ref(self)
		old = self.children[side]
		self._children[side] = child
		old._parent_ref = ref(NULL)
		return old

	def give(self: S, side: bool) -> Nullable[S]:
		return self.swap(side, NULL)

	def drop(self, side: bool) -> None:
		self.give(side)
