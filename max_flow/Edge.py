from typing import TypeVar, Generic
from weakref import ref

T = TypeVar('T')

class Edge(Generic[T]):
	def __init__(self, left: T, right: T, capacity: int):
		self._left = ref(left)
		self._right = right
		self.residual = capacity
		self.capacity = capacity
		self.is_active = False

	@property
	def left(self):
		left = self._left()
		if left is None:
			raise RuntimeError('Attempted access on stale Edge')
		return left

	@property
	def right(self):
		return self._right

	@property
	def flow(self):
		return self.capacity - self.residual
