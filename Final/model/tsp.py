import numpy as np
from queue import PriorityQueue
from copy import deepcopy


class Node:
	def __init__(self, adjacency_mat: np.ndarray, visited_points: list[int] = None, current_len: float | int = 0):
		super().__init__()
		self.a_mat = adjacency_mat
		self.visited_points: list[int] = visited_points
		self.path_length = current_len

	def __str__(self):
		return f'path={self.visited_points}, len={self.path_length}'

	def add_point(self, point: int):
		self.path_length += self.a_mat[self.visited_points[-1], point]
		self.visited_points.append(point)
		return self

	# @property
	def lower_bound(self) -> float:
		if len(self.visited_points) == 1:
			lb = np.sum(np.sort(self.a_mat, axis=1)[:, :2] / 2)
			return lb

		lb = np.sum(np.sort(np.delete(self.a_mat.copy(), self.visited_points, axis=0), axis=1)[:, :2] / 2)

		# 首元素
		line: list = self.a_mat[self.visited_points[0]].tolist()
		lb += line.pop(self.visited_points[1])
		lb += np.min(line)
		# 中间元素
		for i in range(len(self.visited_points))[1: -1]:
			lb += self.a_mat[self.visited_points[i], self.visited_points[i - 1]]
			lb += self.a_mat[self.visited_points[i], self.visited_points[i + 1]]
		# 尾元素
		line: list = self.a_mat[self.visited_points[-1]].tolist()
		lb += line.pop(self.visited_points[-2])
		lb += np.min(line)

		return float(lb)


def tsp_branch_and_bound(a_mat: np.ndarray, start_point: int = 0) -> Node:
	point_ids = list(range(a_mat.shape[0]))
	best_node = tsp_greedy(a_mat.copy(), start_point)
	best_node = Node(a_mat, current_len=float('inf'))

	heap = PriorityQueue()
	root = Node(a_mat, visited_points=[start_point])

	heap.put((root.path_length, root))
	while not heap.empty():
		_, node = heap.get(timeout=0.5)
		if node.path_length == len(point_ids) and (node.add_point(start_point).path_length <= best_node.path_length):
			# 如果为叶子结点，路径加入原点；如果比当前最优路径更优，则替换当前最优路径，否则跳过
			best_node = node
		elif node.lower_bound() < best_node.path_length:
			# 如果节点下界小于当前最优解长度，合格，生成该节点的子节点，所有子节点入队
			for i in range(len(point_ids)):
				if i not in node.visited_points:
					new_node = deepcopy(node).add_point(i)
					# new_node = Node(a_mat, node.visited_points, node.path_length)
					# new_node.add_point(i)
					heap.put((new_node.path_length, new_node))

	return best_node


def tsp_greedy(a_mat: np.ndarray, start_point: int = 0) -> Node:
	path = [start_point]
	path_len = 0
	num_point = a_mat.shape[0]
	while len(path) != num_point:
		p = path[-1]
		path_len += np.min(a_mat[p])
		path.append(np.argmin(a_mat[p]))
		a_mat[:, p] = float('inf')
	# return to start
	path_len += a_mat[start_point, path[-1]]
	path.append(start_point)

	return Node(a_mat, path, path_len)


if __name__ == '__main__':
	print("======================= Test TSP =======================")
	# distances = np.array([
	# 	[float('inf'), 2, 9, 10],
	# 	[1, float('inf'), 6, 4],
	# 	[15, 7, float('inf'), 8],
	# 	[6, 3, 12, float('inf')]
	# ])
	distances = np.array([
		[float('inf'), 1, 15, 6],
		[1, float('inf'), 6, 3],
		[15, 6, float('inf'), 12],
		[6, 3, 12, float('inf')],
	])

	best_node = tsp_branch_and_bound(distances)
	print("best path:", best_node.visited_points)
	print("shortest len:", best_node.path_length)
