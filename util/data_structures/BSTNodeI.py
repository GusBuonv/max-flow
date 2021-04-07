from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple, Optional, TypeVar, List, Protocol
from weakref import ref
import weakref
from ..types import Nullable
from ..constants import NULL, LEFT, RIGHT
from ..type_guards import is_null

S = TypeVar('S', bound='BSTNodeI')

class BSTNodeI(Protocol, metaclass=ABCMeta):
	@property
	@abstractmethod
	def children(self: S) -> List[Nullable[S]]: ...

	@property
	@abstractmethod
	def parent(self: S) -> Nullable[S]: ...

	@property
	@abstractmethod
	def left(self: S) -> Nullable[S]: ...

	@property
	@abstractmethod
	def right(self: S) -> Nullable[S]: ...

	@abstractmethod
	def swap(self: S, side: bool, child: Nullable[S]) -> Nullable[S]: ...

	@abstractmethod
	def give(self: S, side: bool) -> Nullable[S]: ...
