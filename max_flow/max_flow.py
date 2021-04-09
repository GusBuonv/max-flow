from typing import List, Optional, cast
from util.constants import NULL
from max_flow.is_node import is_node
from max_flow.Edge import Edge
from max_flow.PathTree import PathTree
import numpy as np

def max_flow(s_i: int, t_i: int, C: List[List[int]], MAX_FLOW: int) -> int:
	# Initialize graph
	n = len(C)
	nodes = [PathTree(u_i) for u_i in range(n)]
	level_graph: List[set[PathTree]] = [set() for u_i in range(n)]
	levels = cast(List[Optional[int]], [None] * n)
	source: Optional[PathTree] = None
	sink: Optional[PathTree] = None
	for u_i in range(n):
		u = nodes[u_i]
		edges = [Edge(u, nodes[v_i], C[u_i][v_i]) for v_i in range(n) if C[u_i][v_i]]
		[u.add_exiting(edge) for edge in edges]
		if u_i is s_i:
			levels[u_i] = 0
			source = u
		elif u_i is t_i: sink = u
	flow_graph = [[0 for i in range(n)] for i in range(n)]

	# Safety checks
	if source is None: raise RuntimeError('Failed to assign source during graph creation')
	if sink is None: raise RuntimeError('Failed to assign sink during graph creation')

	# Find level graphs and solve for blocking flow while a path exists to the sink
	i = 0
	flow = 0
	level = level_graph[i]
	level.add(source)
	while len(level) > 0:
		do_solve = False
		i += 1

		# Search breadth of current level
		for u in level:
			for uv in u.exiting:
				if uv.residual:
					v = uv.right
					v_i = v.label
					v_level = levels[v_i]
					if (v_level is None) or v_level == i:
						level_graph[i].add(v)
						levels[v_i] = i
						uv.is_active = True
						if v_i is t_i:
							do_solve = True
				else:
					dead = u.remove_exiting(uv, flow_graph, False)
					[nodes.remove(d) for d in dead]
					if u is source:
						flow += uv.flow

		if len(level_graph[i]) == 0:
			break
		elif do_solve:
			i = 0
			flow += find_blocking_flow(source, sink, nodes, flow_graph, MAX_FLOW)
			[level.clear() for level in level_graph]
			level_graph[i].add(source)
			levels = cast(List[Optional[int]], [None] * n)
			levels[s_i] = 0
			level = level_graph[i]
		else:
			level = level_graph[i]

	for e in source.exiting:
		flow += e.flow

	for u in nodes:
		while len(u.exiting) > 0:
			uv = u.exiting.pop()
			u.exiting.append(uv)
			dead = u.remove_exiting(uv, flow_graph, False)
			[nodes.remove(d) for d in dead]

	print(np.matrix(flow_graph))
	return flow

# Blocking flow solver
def find_blocking_flow(s: PathTree, t: PathTree, graph: List[PathTree], flow_graph, MAX_FLOW: int) -> int:
	flow = 0
	t.delta_cost = MAX_FLOW
	while True:
		v = s.find_root()
		if v is t: # Augment
			v = s.find_min()
			d = v.find_cost()
			s.add_cost(-d)
			v = s.find_min()
			while v.find_cost() == 0:
				r = v.cut()
				if is_node(r):
					w = r.find_stem()
				elif v is s:
					break
				else:
					raise RuntimeError('Invalid min cost node')
				vw = next(filter(lambda vx: vx.right is w, v.exiting), None)
				if vw is None:
					raise RuntimeError('Tree edge lacks corresponding graph edge')
				if v is s:
					flow += vw.capacity
				vw.residual = 0
				dead = v.remove_exiting(vw, flow_graph, True)
				[graph.remove(d) for d in dead]
				v = s.find_min()
		else:
			vw = v.active_exit
			if vw is None:
				if v is s:
					break
				while (uv := v.active_entrance):
					u = uv.left
					u.find_root()
					d = u.find_cost()
					uv.residual = d
					u.cut()
					u.add_cost(-d)
					uv.is_active = False
			else:
				w = vw.right
				v.add_cost(vw.residual)
				v.link(w)

	for v in graph:
		while (uv := v.active_entrance):
			uv.residual = v.find_cost()
			uv.is_active = False
			uv.left.cut()
		v.delta_cost = 0
		v.delta_min = 0

	return flow