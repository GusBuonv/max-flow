import weakref

# T = TypeVar('T')
RIGHT = True
LEFT = False

class Node: # type: Node[T]
	def __init__(self, value):
		# type: (T) -> None
		self.value = value
		self.parent_ref = None # type: Optional[weakref.ref[Node[T]]]
		self.children = [None, None] # type: List[Optional[Node[T]]]

	def get_parent(self):
		# type: () -> Optional[Node[T]]
		return self.parent_ref() if self.parent_ref else None

	def get_left(self):
		# type: () -> Optional[Node[T]]
		return self.children[LEFT]

	def get_right(self):
		# type: () -> Optional[Node[T]]
		return self.children[RIGHT]

	def attach(self, side, child):
		# type: (bool, Optional[Node[T]]) -> None

		# `weakref` prevents nodes from keeping one another alive. As soon as
		# the root node no longer has an external reference, the whole structure
		# can be deleted in garbage cleanup without leaks.
		if child:
			child.parent_ref = weakref.ref(self)
		self.children[side] = child

	def is_on(self, side):
		# type: (bool) -> Optional[bool]
		return self.get_parent() and self is self.get_parent().children[side]

	def get_side(self):
		# type: (bool) -> Optional[bool]
		return self.is_on(RIGHT)

def rotate(child, parent, side, side_0):
	# type: (Node[T], Node[T], bool, bool) -> None
	save = child.children[side_0]
	child.attach(side_0, parent)
	parent.attach(side, save)

class SplayTree: # type: SplayTree[T]
	def __init__(self, root = None):
		# type: (Optional[Node[T]]) -> None
		if root:
			root.parent_ref = None
		self.root = root

	def search(self, item):
		# type: (T) -> (Optional[Node[T]], Optional[Node[T]], Optional[bool])
		if self.root is None:
			return (None, None, None)

		parent = None
		side = None
		node = self.root
		while node: # Always true on 1st iteration
			if node.value == item:
				break

			parent = node
			side = item > node.value
			node = node.children[side]

		return (node, parent, side)

	def access(self, item):
		# type: (T) -> Optional[Node[T]]
		(node, parent, branch) = self.search(item)

		if node is None:
			if parent:
				self.splay(parent)

			return

		self.splay(node)
		return node

	def join(self, right):
		# type: (SplayTree[T]) -> SplayTree[T]
		"""Subsumes one SplayTree into another.

		The provided tree MUST consist only of elements larger than those in the
		target tree. NO CHECKS ARE PERFORMED. It is the responsibility of the
		user to ensure the condition is met. If it is not met, the target tree
		will no longer be valid, but no exception will be thrown.

		NOTE: The provided tree is deleted by this operation."""
		if self.root is None:
			self.root = right.root
			del right
			return self

		if right.root is None:
			del right
			return self

		parent = None
		node = self.root
		while node:
			parent = node
			node = parent.get_right()

		self.splay(parent)
		self.root.attach(RIGHT, right.root)
		del right
		return self

	def insert(self, item):
		# type: (T) -> SplayTree[T]
		(node, parent, side) = self.search(item)

		if node:
			raise ValueError('Value already in tree')

		new_node = Node(item)
		if parent is None: # The tree is currently empty
			self.root = new_node
			return self
		parent.attach(side, new_node)
		self.splay(new_node)
		return self

	def delete(self, item):
		# type: (T) -> SplayTree[T]
		(node, parent, side) = self.search(item)

		if node is None:
			raise ValueError('Value not in tree')

		left = SplayTree(node.get_left())
		right = SplayTree(node.get_right())
		left.join(right)
		if parent:
			parent.attach(side, left.root)
			self.splay(parent)
		else:
			self.root = left.root
		return self

	def splay(self, node):
		# type: (Node[N]) -> None
		if self.root is node:
			return

		while True:
			side = node.get_side()
			if side is None:
				raise ValueError('Bad parent reference in tree')

			side_0 = not side
			parent = node.get_parent()
			grand_parent = parent.get_parent()

			if grand_parent is None: # 'Zig' Operation
				rotate(node, parent, side, side_0)
				break

			great_grand_parent = grand_parent.get_parent()
			upper_side = grand_parent.get_side()
			if parent.is_on(side): # 'Zig-Zig' Operation
				rotate(parent, grand_parent, side, side_0)
				rotate(node, parent, side, side_0)
			else: # 'Zig-Zag' Operation
				rotate(node, parent, side, side_0)
				rotate(node, grand_parent, side_0, side)

			if great_grand_parent:
				great_grand_parent.attach(upper_side, node)
			else:
				break

		node.parent_ref = None
		self.root = node
		return
