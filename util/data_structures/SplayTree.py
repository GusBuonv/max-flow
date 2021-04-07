from typing import TypeVar, Generic, Tuple, Protocol
from abc import abstractmethod
from weakref import ref
from util.constants import LEFT, NULL, RIGHT
from util.types import Nullable
from util.type_guards import is_null
from util.data_structures.SplayTreeNode import SplayTreeNode
from util.data_structures.is_node import is_node

T_co = TypeVar('T_co', covariant=True)
Gt = TypeVar('Gt', bound='SupportsGt')

class SupportsGt(Protocol):
	__slots__ = ()

	@abstractmethod
	def __gt__(self: Gt, x: Gt) -> bool: ...

class SplayTree(Generic[Gt]):
	def __init__(self, node: Nullable[SplayTreeNode[Gt]] = NULL):
		if is_node(node.parent):
			raise RuntimeError('Cannot initialize a splay tree from a non-root node')

		self.root = node

	@staticmethod
	def join(left: 'SplayTree[Gt]', right: 'SplayTree[Gt]') -> 'SplayTree[Gt]':
		"""Subsumes one SplayTree into another.

		The provided tree MUST consist only of elements larger than those in the
		target tree. NO CHECKS ARE PERFORMED. It is the responsibility of the
		user to ensure the condition is met. If it is not met, the target tree
		will no longer be valid, but no exception will be thrown.

		NOTE: The input trees are deleted by this operation."""
		if is_null(right.root):
			joint = SplayTree(left.root)
		elif is_node(left.root):
			parent = left.root
			node = parent.right
			while is_node(node):
				parent = node
				node = node.right

			left._splay(parent)
			left.root.swap(RIGHT, right.root)
			joint = SplayTree(left.root)
		else: # left.root is NULL
			joint = SplayTree(right.root)

		del left, right
		return joint

	def access(self, item: Gt) -> Nullable[SplayTreeNode[Gt]]:
		(node, parent, side) = self._search(item)

		if is_node(node):
			pass
		elif is_node(parent):
			node = parent
		else: # node is NULL and parent is NULL –> tree is empty
			return node

		self._splay(node)
		return node

	def insert(self, item: Gt) -> 'SplayTree[Gt]':
		(node, parent, side) = self._search(item)

		if is_node(node):
			raise ValueError('Value already in tree')

		new_node = SplayTreeNode(item)
		if is_null(parent): # node is NULL and parent is NULL –> tree is empty
			self.root = new_node
		else:
			parent.swap(side, new_node)
			self._splay(new_node)

		return self

	def delete(self, item: Gt) -> 'SplayTree[Gt]':
		(node, parent, side) = self._search(item)

		if is_null(node):
			raise ValueError('Value not in tree')

		left: SplayTree[Gt] = SplayTree(node.give(LEFT))
		right: SplayTree[Gt]  = SplayTree(node.give(RIGHT))
		replacement = SplayTree.join(left, right).root

		if is_node(parent):
			parent.swap(side, replacement)
			self._splay(parent)
		else: # node is NULL and parent is NULL –> tree is empty
			self.root = replacement

		return self

	def _search(self, value: Gt) -> Tuple[Nullable[SplayTreeNode[Gt]], Nullable[SplayTreeNode[Gt]], bool]:
		node = self.root
		parent = NULL
		side = False
		while is_node(node):
			if node.value == value:
				break

			side = value > node.value
			parent = node
			node = node.children[side]

		return (node, parent, side)

	def _splay(self, node: SplayTreeNode[Gt]) -> None:
		if node is self.root:
			return

		lookAhead = node.rotate()
		while (lookAhead := node.rotate(lookAhead)):
			pass

		self.root = node
		return
