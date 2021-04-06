import weakref

RIGHT = True
LEFT = False

class NullNode:
	_middle = type("", (), dict(append=staticmethod(lambda *x : None)))

	def __init__(self):
		pass

	def get_parent(self):
		pass

	def set_parent(self, node):
		pass

	def get_delta_cost(self):
		return 0

	def set_delta_cost(self, value):
		pass

	def get_cost(self):
		return 0

	def get_delta_min(self):
		return 0

	def set_delta_min(self, value):
		pass

	def get_min(self):
		return 0

	def get_left(self):
		return self

	def get_right(self):
		return self

	def get_child(self, side):
		return self

	def attach(self, side, child):
		pass

	def remove_middle(self, middle_child):
		pass

	def set_as_middle_of(self, parent):
		pass

	def is_on(self, side):
		return False

	def get_side(self):
		return None

NULL_NODE = NullNode()

class Edge:
	def __init__(self, left, right):
		# type: (Node, Node, int) -> None
		self.left = left
		self.right = right
		self.flow = 0

class Vertex:
	def __init__(self, node, id):
		# type: (Node, int) -> None
		self.exiting = [] # List[Edge]
		self.entering = [] # List[Edge]
		self.node = node
		self.id = id

class Node: # type: Node
	def __init__(self, id):
		# type: (int) -> None
		self._parent = NULL_NODE # Union[Node, NULL_NODE]
		self._children = [NULL_NODE, NULL_NODE] # type: List[Union[Node, NULL_NODE]]
		self._middle = [] # type: List[Node]
		self.vertex = Vertex(self, id)
		self._delta_cost = 0
		self._delta_min = 0

	def get_parent(self):
		# type: () -> Union[Node, NULL_NODE]
		return self._parent

	def set_parent(self, node):
		# type: (Node) -> None
		self._parent = node

	def get_delta_cost(self):
		return self._delta_cost

	def set_delta_cost(self, value):
		# type: (int) -> None
		self._delta_cost = value

	def get_cost(self):
		# type: () -> int
		cost = self._delta_cost
		if self.get_side() is not None: # Not at the root of a solid sub-tree
			cost += self.get_parent().get_cost()

		return cost

	def get_delta_min(self):
		return self._delta_min

	def set_delta_min(self, value):
		# type: (int) -> None
		self._delta_min = value

	def get_min(self):
		# type: () -> int
		return self.get_cost() - self._delta_min

	def get_left(self):
		# type: () -> Union[Node, NULL_NODE]
		return self._children[LEFT]

	def get_right(self):
		# type: () -> Union[Node, NULL_NODE]
		return self._children[RIGHT]

	def get_child(self, side):
		# type: (bool) -> Node
		return self._children[side]

	def attach(self, side, child):
		# type: (bool, Union[Node, NULL_NODE]) -> None

		# `weakref` prevents nodes from keeping one another alive. As soon as
		# the root node no longer has an external reference, the whole structure
		# can be deleted in garbage cleanup without leaks.
		child.set_parent(self)
		self._children[side] = child

	def remove_middle(self, middle_child):
		# type: (Node) -> None
		self._middle.remove(middle_child)

	def set_as_middle_of(self, parent):
		# type: (Optional[Node]) -> None
		self.set_parent(parent)
		parent._middle.append(self)

	def pop_middle(self):
		if len(self._middle) > 0:
			return self._middle.pop()

	def is_on(self, side):
		# type: (bool) -> bool
		return self is self.get_parent().get_child(side)

	def get_side(self):
		# type: (bool) -> Optional[bool]
		right = self.is_on(RIGHT)
		if right:
			return RIGHT

		left = self.is_on(LEFT)
		return LEFT if left else None

def rotate(v, w, side, side_0):
	# type: (Node, Node, bool, bool) -> None
	a = v.get_child(side)
	b = v.get_child(side_0)
	c = w.get_child(side_0)
	ww = w.get_parent()
	w_side = w.get_side()
	v.attach(side_0, w)
	w.attach(side, b)
	if w_side is None:
		if ww is not NULL_NODE:
			ww.remove_middle(w)
			v.set_as_middle_of(ww)
		else:
			v.set_parent(NULL_NODE)
	else:
		ww.attach(w_side, v)
	old_v_delta_cost = v.get_delta_cost()
	v.set_delta_cost(old_v_delta_cost + w.get_delta_cost())
	w.set_delta_cost(-old_v_delta_cost)
	b.set_delta_cost(old_v_delta_cost + b.get_delta_cost())
	w.set_delta_min(max(0, b.get_delta_min() - b.get_delta_cost(), c.get_delta_min() - c.get_delta_cost()))
	v.set_delta_min(max(0, a.get_delta_min() - a.get_delta_cost(), w.get_delta_min() - w.get_delta_cost()))

def splice(v, w):
	# type: (Node, Node) -> None
	w.remove_middle(v)
	u = w.get_left()
	u.set_as_middle_of(w)
	w.attach(LEFT, v)
	v.set_delta_cost(v.get_delta_cost() - w.get_delta_cost())
	u.set_delta_cost(u.get_delta_cost() + w.get_delta_cost())
	wr = w.get_right()
	w.set_delta_min(max(0, v.get_delta_min() - v.get_delta_cost(), wr.get_delta_min() - wr.get_delta_cost()))

def find_cost(node):
	# type: (Node) -> int
	splay(node)
	return node.get_cost()

def find_root(node):
	# type: (Node) -> Node
	splay(node)
	right = node.get_right()
	while right is not NULL_NODE:
		node = right
		right = node.get_right()
	splay(node)
	return node

def find_min(node):
	# type: (Node) -> Node
	while True:
		right = node.get_right()
		left = node.get_left()
		right_diff = right.get_delta_cost() - right.get_delta_min() + node.get_delta_min()
		if right is not NULL_NODE and right_diff == 0:
			node = right
		elif (right is NULL_NODE or right_diff > 0) and node.get_delta_min() > 0:
			node = left
		else:
			break
	splay(node)
	return node

def add_cost(node, cost):
	# type: (Node, int) -> None
	splay(node)
	node.set_delta_cost(cost + node.get_delta_cost())
	left = node.get_left()
	if left is not NULL_NODE:
		left.set_delta_cost(left.get_delta_cost() - cost)

def link(v, w):
	# type: (Node, Node) -> None
	splay(v)
	splay(w)
	v.set_as_middle_of(w)

def cut(v):
	splay(v)
	right = v.get_right()
	right.set_delta_cost(v.get_delta_cost() + right.get_delta_cost())
	v.attach(RIGHT, NULL_NODE)
	right.set_parent(NULL_NODE)

def splay(node):
	# type: (Node) -> None
	parent = node.get_parent()
	while parent is not NULL_NODE:
		side = node.get_side()
		if side is None:
			splice(node, parent)
			rotate(node, parent, LEFT, RIGHT)
		else:
			side_0 = not side
			side_p = parent.get_side()
			if side_p is None: # 'Zig' Operation
				rotate(node, parent, side, side_0)
			else:
				grand_parent = parent.get_parent()
				if side is side_p: # 'Zig-Zig' Operation
					rotate(parent, grand_parent, side, side_0)
					rotate(node, parent, side, side_0)
				else: # 'Zig-Zag' Operation
					rotate(node, parent, side, side_0)
					rotate(node, grand_parent, side_0, side)

		parent = node.get_parent()

def make_trees(graph):
	# type: (int, int, List[List[int]]) -> List[Node]
	nodes = [None] * len(graph)
	for i in range(len(graph)):
		if bool(sum(graph[i])):
			if nodes[i] is None:
				nodes[i] = Node(i)
			for j in range(len(graph)):
				if graph[i][j] > 0:
					if nodes[j] is None:
						nodes[j] = Node(j)
					edge = Edge(nodes[i], nodes[j])
					nodes[i].vertex.exiting.append(edge)
					nodes[j].vertex.entering.append(edge)

	return nodes

def solution(source, sink, cap):
	# type: (int, int, List[List[int]]) -> int
	nodes = make_trees(cap)
	flow = 0
	s = nodes[source]
	t = nodes[sink]
	while True:
		v = find_root(s)
		if v is t: # Augment
			v = find_min(s)
			c = find_cost(v)
			add_cost(s, -c)
			while find_cost(v) == 0: # Delete
				right = v.get_right()
				if right is NULL_NODE:
					raise RuntimeError('Augmenting path cannot terminate prior to sink')

				found = False
				for edge in v.vertex.exiting:
					vr = edge.right
					if vr is right:
						found = True
						break
				if not found:
					raise RuntimeError('Failed to locate the exiting edge')
				v.vertex.exiting.remove(edge)
				vr.vertex.entering.remove(edge)
				cut(v)
				i = v.vertex.id
				j = vr.vertex.id
				flow += cap[i][j]
				v = find_min(s)
		else:
			if len(v.vertex.exiting) > 0: # Advance
				edge = v.vertex.exiting.pop()
				i = edge.left.vertex.id
				j = edge.right.vertex.id
				add_cost(v, cap[i][j])
				link(v, edge.right)
				v.vertex.exiting.append(edge)
			elif v is s: # Terminate
				for u in nodes:
					p_u = u.get_parent()
					if p_u is not NULL_NODE:
						while len(u.vertex.exiting) > 0:
							edge = u.vertex.exiting.pop()
							v = edge.right
							if p_u is v:
								cut(u)
								d = find_cost(u)
								add_cost(u, -d)
								i = u.vertex.id
								j = v.vertex.id
								flow += cap[i][j] - d
								break
				return flow
			else: # Retreat
				while len(v.vertex.entering) > 0:
					edge = v.vertex.entering.pop()
					u = edge.left
					u.vertex.exiting.remove(edge)
					if u is v.get_parent():
						cut(u)
						d = find_cost(u)
						add_cost(u, -d)
						i = u.vertex.id
						j = v.vertex.id
						flow += cap[i][j] - d
