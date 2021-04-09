from typing import List

def normalize_flow_graph(s: List[int], t: List[int], C: List[List[int]]):
	# Copy capacity matrix
	C_n = [[C[i][j] for j in range(len(C))] for i in range(len(C))]

	# Initialize source
	n = len(C_n)
	if len(s) == 1:
		s_n = s[0]
	else:
		s_n = n
		n += 1
		[row.append(0) for row in C_n]
		C_n.append([sum(C[v_i]) if v_i in s else 0 for v_i in range(n)])

	# Initialize sink
	if len(t) == 1:
		t_n = t[0]
	else:
		[C_n[u_i].append(sum([row[u_i] for row in C_n])) if u_i in t else C_n[u_i].append(0) for u_i in range(n)]
		t_n = n
		n += 1
		C_n.append([0] * n)

	return (s_n, t_n, C_n)
