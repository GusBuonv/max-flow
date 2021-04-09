# from max_flow.max_flow import max_flow
from max_flow.rework import find_max_flow
from random import randrange
from max_flow.third_party_code.verified import verified_solution
from max_flow.normalize_flow_graph import normalize_flow_graph
import time

caps = [[0, 2], [0, 0]]
sources = [0]
sinks = [1]
(s, t, C) = normalize_flow_graph(sources, sinks, caps)
print("  Test trivial flow from source directly to sink:")
flow = find_max_flow(s, t, C)
correct = 2
print(f"    Result is {flow} – expected {correct} – {'✅' if flow == correct else '❌'}")

caps = [[0, 7, 0, 0],
		[0, 0, 6, 0],
		[0, 0, 0, 8],
		[0, 0, 0, 0]]
sources = [0]
sinks = [3]
(s, t, C) = normalize_flow_graph(sources, sinks, caps)
print("  Test multi-node, single-path flow:")
flow = find_max_flow(s, t, C)
correct = 6
print(f"    Result is {flow} – expected {correct} – {'✅' if flow == correct else '❌'}")

caps = [[ 0, 3, 3, 0, 0, 0 ],
		[ 0, 0, 2, 3, 0, 0 ],
		[ 0, 0, 0, 0, 2, 0 ],
		[ 0, 0, 0, 0, 4, 2 ],
		[ 0, 0, 0, 0, 0, 2 ],
		[ 0, 0, 0, 0, 0, 0 ]]
sources = [0]
sinks = [5]
(s, t, C) = normalize_flow_graph(sources, sinks, caps)
print("  Test acyclic multi-node, multi-path flow:")
flow = find_max_flow(s, t, C)
correct = 4
print(f"    Result is {flow} – expected {correct} – {'✅' if flow == correct else '❌'}")

caps = [[0, 0, 4, 6, 0, 0],
		[0, 0, 5, 2, 0, 0],
		[0, 0, 0, 0, 4, 4],
		[0, 0, 0, 0, 6, 6],
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0]]
sources = [0, 1]
sinks = [4, 5]
(s, t, C) = normalize_flow_graph(sources, sinks, caps)
print("  Test multi-source, multi-sink, multi-path, acyclic flow:")
flow = find_max_flow(s, t, C)
correct = 16
print(f"    Result is {flow} – expected {correct} – {'✅' if flow == correct else '❌'}")

# # Issue problem
# caps = [[1321133, 395372, 957723, 106527, 276606, 1383355], [875848, 299757, 165320, 796014, 1342298, 1770557], [698417, 1268211, 1315598, 1949408, 1935813, 1561009], [1405529, 1113099, 1681843, 85185, 1766392, 135347], [1975292, 739290, 454722, 1153202, 242251, 722870], [106120, 1495921, 1886925, 603969, 1013272, 172767]]
# sources = [2, 4]
# sinks = [5]
# (s, t, C) = normalize_flow_graph(sources, sinks, caps)
# print("  Test multi-source, multi-sink, multi-path, acyclic flow:")
# correct = verified_solution(s, t, C)
# flow = find_max_flow(s, t, C)
# print(f"    Result is {flow} – expected {correct} – {'✅' if flow == correct else '❌'}")

# Random problem
MAX_FLOW = 2000000
n = randrange(6) + 2
caps = [[randrange(MAX_FLOW) for i in range(n)] for i in range(n)]
sources_raw = [randrange(n) for i in range(randrange(n - 1) + 1)]
source_set = set(sources_raw)
sources = list(source_set)
sink_set = set([randrange(n) for i in range(randrange(n) + 1)])
disjoint_sinks = sink_set.difference(source_set)
while len(disjoint_sinks) == 0:
	sink_set = set([randrange(n) for i in range(randrange(n) + 1)])
	disjoint_sinks = sink_set.difference(source_set)
sinks = list(disjoint_sinks)
print("  Test random problem:")
(s, t, C) = normalize_flow_graph(sources, sinks, caps)
start = time.time()
flow = find_max_flow(s, t, C)
stop = time.time()
print(f"    Dinic's execution time: {stop - start}s")
start = time.time()
correct = verified_solution(s, t, C)
stop = time.time()
print(f"    Push-Relabel execution time: {stop - start}s")
print(f"    Result is {flow} – expected {correct} – {'✅' if flow == correct else '❌'}")
