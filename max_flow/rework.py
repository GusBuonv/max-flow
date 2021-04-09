from typing import List, Literal, Optional, Tuple, Set, Callable
from max_flow.PathTreeRework import PathTree
from util.data_structures.is_node import is_node

Edge = Tuple[int, int, bool]
LevelGraph = List[List[Edge]]

def find_max_flow(s: int, t: int, C: List[List[int]]) -> int:
	"""Find the maximum flow possible in a single-source, single-sink network."""

	# Initialize residuals matrix
	n = len(C)
	R = [[C[i][j] for j in range(n)] for i in range(n)] # Residual capacity matrix

	# Initialize level graph
	exits: LevelGraph = [[] for i in range(n)]
	entrances: List[List[int]] = [[] for i in range(n)]
	level_of: List[Optional[int]] = [None for i in range(n)]
	levels: List[Set[int]] = [set() for i in range(n)]
	levels[0].add(s)
	level_of[s] = 0
	i = 0 # Current level
	ii = 1 # Next level

	""" UTILITY FUNCTIONS """
	def F(u: int, v: int) -> int:
		"""Flow along an edge (u, v)."""
		return C[u][v] - R[u][v]

	def is_on_level(u: int, i: int) -> bool:
		"""Check if a node is on a given level."""
		return level_of[u] is None or level_of[u] is i

	def set_level_of(u: int, i) -> Literal[True]:
		""""Update the level of a node."""
		level_of[u] = i
		levels[i].add(u)
		return True

	def set_entrance(u: int, v: int) -> Literal[True]:
		"""Update the entrance list for a node v based on the edge (u, v)."""
		entrances[v].append(u)
		return True

	def update_edge(u: int, uv: Edge, d: int) -> None:
		"""Update the flow along an edge."""
		v = uv[0]
		if uv[2]:
			# Edge traverses backwards
			R[v][u] = C[v][u] - d
		else:
			R[u][v] = d

	def has_capacity(u: int, v: int) -> int:
		"""Returns capacity of an edge, prioritizing outgoing capacity."""
		return R[u][v] or (R[v][u] and F(v, u))

	def is_reverse(u: int, v: int) -> bool:
		"""Checks whether an edge traverses backwards."""
		return not R[u][v]

	"""
	MAIN LOOP:

	Construct and solve level graphs until no path exists from source to
	sink. We recognize this is the case when we construct a level containing
	no nodes before we construct a level containing the sink.
	"""
	while len(levels[i]) > 0:
		# Construct the next level
		for u in levels[i]:
			exits[u] = [
				set_level_of(v, ii)
				and set_entrance(u, v)
				and (v, c, is_reverse(u, v))
				for v in range(n)
				if is_on_level(v, ii)
				and (c := has_capacity(u, v))
			]

		if level_of[t] == ii:
			# Solve the level graph by sending a blocking flow along it
			send_blocking_flow(s, t, exits, entrances, update_edge)

			# Reset the level graph
			for level in levels:
				level.clear()
			for entrance in entrances:
				entrance.clear()
			# Exits are overwritten, and so don't need to be cleared
			level_of = [None for i in range(n)]
			level_of[s] = 0
			levels[0].add(s)
			i = 0
			ii = 1
		else:
			i = ii
			ii += 1

	# Sum and return flow
	return sum((F(s, v) for v in range(n)))

def send_blocking_flow(
		s_i: int,
		t_i: int,
		exits: LevelGraph,
		entrances: List[List[int]],
		update_edge: Callable[[int, Edge, int], None]
	) -> None:
	"""
	Finds and sends a blocking flow along a level graph.

	A blocking flow is both the maximum possible flow in a level graph and one
	that eliminates all possible paths from source to sink.
	"""
	# HIGH = 20000000
	n = len(exits)
	forest = [PathTree(i) for i in range(n)]
	s = forest[s_i]
	t = forest[t_i]
	# t.add_cost(HIGH)

	def find_edge(u: int, v: Optional[int] = None) -> Optional[Edge]:
		if v is not None:
			return next(filter(lambda ux: ux[0] == v, exits[u]), None)
		elif len(exits[u]) > 0:
			return exits[u][-1]

	def remove_edge(u: PathTree, v: PathTree, d: Optional[int] = None):
		uv = find_edge(u.label, v.label)
		if uv is None:
			raise RuntimeError('Tree edge lacks corresponding graph edge')
		if d is not None:
			update_edge(u.label, uv, d)
		exits[u.label].remove(uv)
		entrances[v.label].remove(u.label)

	def remove_saturated_edge(u):
		d = u.find_cost()
		v = u.next_in_path
		u.cut()
		if is_node(v):
			remove_edge(u, v, d)
		elif u is s:
			return v
		else:
			raise RuntimeError('Edge not on path')
		return s.find_min()

	while True:
		v = s.find_root()
		if v is t:
			# Update: send flow
			v = s.find_min()
			d = v.find_cost()
			s.add_cost(-d)

			# Trim saturated branches
			v = s.find_min()
			v = remove_saturated_edge(v)
			while v.find_cost() == 0:
				v = remove_saturated_edge(v)
		elif (vw := find_edge(v.label)):
			# Advance: extend tree
			w = vw[0]
			d = vw[1]
			v.add_cost(d)
			v.link(forest[w])
		elif v is not s:
			# Retreat: trim tree
			while len(entrances[v.label]):
				u_i = entrances[v.label][-1]
				u = forest[u_i]
				uu = u.next_in_path
				if v is uu:
					d = u.find_cost()
					u.cut()
					u.add_cost(-d)
					remove_edge(u, v, d)
				else:
					remove_edge(u, v)
		else:
			break

	for u in forest:
		v = u.next_in_path
		if is_node(v):
			remove_edge(u, v, u.find_cost())
			u.cut()
