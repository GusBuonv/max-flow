# Push-Relabel Algorithm for Maximum Flow
#
# Complexity: O(n**2 * m) | n = number of nodes; m = number of edges;
#
# Room for improvement:
#
#   Highest Label Node Selection: O(n**2 * sqrt(m)) Dinic's Algo w/Link-Cut
#   Trees: O(n * log(n) * m) | Only preferable in select circumstances
#
# Why this Algo:
#
#   * Simpler structure than Dinic's
#   * Ford-Fulkerson would crumple under O(F * m)
# 		| Worst case: F = 2000000; m = 2500; O(50000000000)
#

def verified_solution(source, sink, caps):
	n = len(caps) # C is the capacity matrix
	used = [[0] * n for i in range(n)]

	height = [0] * n # distance from node to sink
	excess = [0] * n # surplus of incoming flow over outgoing flow
	seen   = [0] * n # neighbors seen since last relabel
	queue  = [i for i in range(n) if i != source and i != sink]

	# Push flow along the edge
	def push(u, v):
		residual = caps[u][v] - used[u][v]
		send = min(excess[u], residual)
		used[u][v] += send
		used[v][u] -= send # Update backwards flow
		excess[u] -= send
		excess[v] += send

	def relabel(u):
		min_height = float('inf')
		for v in range(n):
			if caps[u][v] - used[u][v] > 0:
				min_height = min(min_height, height[v])
				height[u] = min_height + 1

	def discharge(u):
		while excess[u] > 0:
			if seen[u] < n:
				# Check next neighbor.
				v = seen[u]
				has_residual = caps[u][v] - used[u][v] > 0
				if has_residual and height[u] > height[v]:
					push(u, v)
				else:
					seen[u] += 1
			else:
				# All neighbors expended. Time to relabel.
				relabel(u)
				seen[u] = 0

	# Source cannot be further than n nodes from sink.
	height[source] = n
	# No limit on reserves in the source.
	excess[source] = float("inf")
	for v in range(n):
		push(source, v)

	p = 0
	while p < len(queue):
		u = queue[p]
		old_height = height[u]
		discharge(u)
		if height[u] > old_height:
			# Set tail of queue at head
			queue.insert(0, queue.pop(p))
			# Reset queue index
			p = 0
		else:
			p += 1
	return sum(used[source])
