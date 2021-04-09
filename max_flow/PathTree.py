from max_flow.Edge import Edge
from typing import List, Optional, Tuple, cast, Any
from weakref import ref
from max_flow.is_node import is_node
from util.constants import LEFT, NULL, RIGHT
from util.type_guards import is_null
from util.types import Nullable

class PathTree: # type: Node
	def __init__(self, label: int):
		super().__init__()
		self.delta_cost: int = 0
		self.delta_min: int = 0
		self.parent: Nullable[PathTree] = NULL
		self.children: List[Nullable[PathTree]] = [NULL, NULL]
		self.exiting: List[Edge[PathTree]] = []
		self.entering: List[Edge[PathTree]] = []
		self.label = label
		self.middle: List[PathTree] = []

	def add_exiting(self, edge: Edge['PathTree']) -> None:
		self.exiting.append(edge)
		edge.right.entering.append(edge)

	def remove_exiting(self, edge: Edge['PathTree'], flow_graph: List[List[int]], flag) -> List['PathTree']:
		self.exiting.remove(edge)
		flow_graph[edge.left.label][edge.right.label] = edge.flow
		return edge.right._remove_entering(edge, flow_graph, flag)

	def _remove_entering(self, edge: Edge['PathTree'], flow_graph: List[List[int]], flag) -> List['PathTree']:
		self.entering.remove(edge)
		dead_nodes: List['PathTree'] = []
		if len(self.entering) is 0:
			dead_nodes.append(edge.right)
			while len(self.exiting) > 0:
				e = self.exiting.pop()
				if flag:
					e.left.find_root()
					e.residual = e.left.find_cost()
					e.left.cut()
				flow_graph[e.left.label][e.right.label] = e.flow
				dead_nodes.extend(e.right._remove_entering(e, flow_graph, flag))
		return dead_nodes

	def pop_exiting(self) -> Optional[Edge['PathTree']]:
		if len(self.exiting) > 0:
			edge = self.exiting.pop()
			edge.right.entering.remove(edge)
			return edge

	@property
	def active_exit(self) -> Optional[Edge['PathTree']]:
		def condition(edge: Edge['PathTree']): return edge.is_active
		return next(filter(condition, self.exiting), None)

	@property
	def active_entrance(self) -> Optional[Edge['PathTree']]:
		def condition(edge: Edge['PathTree']): return edge.is_active
		return next(filter(condition, self.entering), None)

	@property
	def left(self) -> Nullable['PathTree']:
		return self.children[LEFT]

	@property
	def right(self) -> Nullable['PathTree']:
		return self.children[RIGHT]

	def is_on(self, side: bool) -> bool:
		return self is self.parent.children[side]

	def swap(self, side: bool, child: Nullable['PathTree']) -> Nullable['PathTree']:
		child.parent = self
		old = self.children[side]
		self.children[side] = child
		old.parent = NULL
		return old

	def give(self, side: bool) -> Nullable['PathTree']:
		return self.swap(side, NULL)

	def drop(self, side: bool) -> None:
		self.give(side)

	@property
	def cost(self) -> int:
		cost = self.delta_cost
		parent = self.parent
		if is_node(parent): # Not at the root of a solid sub-tree
			cost += parent.cost

		return cost

	@property
	def _min(self):
		return self.cost - self.delta_min

	def adopt_middle(self, child: 'PathTree'):
		self.middle.append(child)
		child.parent = self

	@property
	def side(self) -> Optional[bool]:
		parent = self.parent
		if is_null(parent):
			return
		right = self is parent.children[RIGHT]
		if right: return RIGHT
		left = self is parent.children[LEFT]
		if left: return LEFT

	def _rotate(self, lookAhead: Optional[Tuple[Nullable['PathTree'], bool]] = None) -> Optional[Tuple[Nullable['PathTree'], bool]]:
		if lookAhead:
			(parent, side) = lookAhead
		else:
			parent = self.parent
			side = self.side

		if side is None:
			# self is middle child of parent or root
			return

		if is_node(parent):
			# Handle single rotation with parent
			side_0 = not side
			a = self.children[side]
			b = self.give(side_0)
			c = parent.children[side_0]
			parent.swap(side, b) # Detaches self from parent
			grand_parent = parent.parent
			grand_side = parent.side

			# Update costs
			old_delta_cost = self.delta_cost
			self.delta_cost += parent.delta_cost
			parent.delta_cost = - old_delta_cost
			b_diff = 0
			if is_node(b):
				b.delta_cost += old_delta_cost
				b_diff = b.delta_min - b.delta_cost
			c_diff = c.delta_min - c.delta_cost if is_node(c) else 0
			a_diff = a.delta_min - a.delta_cost if is_node(a) else 0
			p_diff = parent.delta_min - parent.delta_cost
			parent.delta_min = max(0, b_diff, c_diff)
			self.delta_min = max(0, a_diff, p_diff)

			# Handle new self parent (i.e. previous grand parent)
			result = None
			if is_node(grand_parent):
				if grand_side is not None:
					# grand parent in same solid sub-tree
					grand_parent.swap(grand_side, self) # Detaches parent from grand_parent
					result = (grand_parent, grand_side)
				else:
					# parent was, and now self is, middle node
					grand_parent.middle.remove(parent)
					grand_parent.adopt_middle(self)

			self.swap(side_0, parent)
			return result

	def _splice(self) -> Optional['PathTree']:
		if self.side is not None:
			return

		parent = self.parent
		if is_node(parent):
			parent.middle.remove(self)
			u = parent.swap(LEFT, self)
			if is_node(u):
				parent.adopt_middle(u)
				u.delta_cost += parent.delta_cost
			self.delta_cost -= parent.delta_cost
			ur = parent.right
			ur_diff = ur.delta_min - ur.delta_cost if is_node(ur) else 0
			s_diff = self.delta_min - self.delta_cost
			parent.delta_min = max(0, s_diff, ur_diff)
			return parent

	def _solid_splay(self) -> Optional['PathTree']:
		lookAhead = self._rotate()
		while (lookAhead := self._rotate(lookAhead)):
			pass
		parent = self.parent
		if is_node(parent):
			return parent

	def _splay(self) -> 'PathTree':
		# Quick exit when root
		if is_null(self.parent):
			return self

		# 1st Pass – Splay the solid sub-trees up to root
		node = self
		while (node := node._solid_splay()):
			pass

		# 2nd Pass – Splice the dashed edges up to root
		if is_null(self.parent):
			return self
		node = self
		while (node := node._splice()):
			pass

		# 3rd Pass – Splay self to root
		self._solid_splay()
		return self

	def find_cost(self) -> int:
		return self._splay().cost

	def find_root(self) -> 'PathTree':
		node = self._splay()
		right = node.right
		while is_node(right):
			node = right
			right = node.right
		return node._splay()

	def find_stem(self) -> 'PathTree':
		node = self._splay()
		left = node.left
		while is_node(left):
			node = left
			left = node.left
		return node._splay()

	def find_min(self) -> 'PathTree':
		# node = self._splay()
		node = self.find_root()
		left = node.left
		if is_node(left):
			node = left
		else: return node

		# n_cost := n_delta_cost  # 1
		# min_cost := n_cost - n_delta_min # 2
		# r_cost := r_delta_cost + n_cost # 3
		# r_cost = r_min_cost + r_delta_min # 2 -> 4
		# r_min_cost + r_delta_min = r_delta_cost + min_cost + n_delta_min # 3 & 4 & 2 -> 5
		# r_min_cost - min_cost = r_delta_cost - r_delta_min + n_delta_min # 5 -> 6
		while True:
			right = node.right
			left = node.left
			if is_node(right):
				r_diff = right.delta_cost - right.delta_min + node.delta_min
				if (r_diff == 0) is True:
					node = cast('PathTree', right)
					continue

			if node.delta_min > 0:
				if is_node(left):
					node = left
					continue
				else:
					raise RuntimeError('Invalid cost data')

			break

		return node._splay()

	def add_cost(self, cost: int) -> None:
		self._splay()
		self.delta_cost += cost
		left = self.left
		if is_node(left):
			left.delta_cost -= cost

	def cut(self) -> Nullable['PathTree']:
		right = self._splay().give(RIGHT)
		if is_node(right):
			right.delta_cost += self.delta_cost
		return right

	def link(self, other: 'PathTree'):
		# pass
		self._splay()
		other._splay()
		other.middle.append(self)
		self.parent = other
