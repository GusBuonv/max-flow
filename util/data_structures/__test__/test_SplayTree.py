from ..SplayTree import SplayTree
from ..is_node import is_node

t = SplayTree().insert(0).insert(50).insert(20).insert(5).insert(30).insert(15).delete(30)
values = []
while is_node(t.root):
	min_node = t.access(0)
	value = min_node.value
	values.append(value)
	t.delete(value)

print('SplayTree:')
print('    Supports insert, delete, access, and join: %s' % '✅' if values == [0, 5, 15, 20, 50] else '❌')
