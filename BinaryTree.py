import math
from typing import List


class TreeNode:
	def __init__(self, index: int, data: List[str], parent=None):
		self.id = index
		self.data = data
		self.parent = parent
		self.left = None
		self.right = None

	def get_left_index(self) -> int:
		if self.left:
			return self.left.id

	def get_right_index(self) -> int:
		if self.right:
			return self.right.id

	def is_leaf(self) -> bool:
		return (not self.left) and (not self.right)

	def __repr__(self):
		return f"TreeNode(id={self.id}, data={self.data})"


class BinaryTree:
	def __init__(self):
		self.root = None
		self.nodes = {}

	def add_node(self, id, data):
		if id == 0:
			if self.root is not None:
				raise ValueError("Root already exists.")
			self.root = TreeNode(id, data)
			self.nodes[id] = self.root
		else:
			parent_id = (id - 1) // 2
			if parent_id not in self.nodes:
				raise ValueError(f"Parent with ID {parent_id} does not exist.")
			parent = self.nodes[parent_id]
			new_node = TreeNode(id, data, parent)
			self.nodes[id] = new_node
			if id % 2 == 1:
				if parent.left is not None:
					raise ValueError(
						f"Node with ID {id} already has a left child.")
				parent.left = new_node
			else:
				if parent.right is not None:
					raise ValueError(
						f"Node with ID {id} already has a right child.")
				parent.right = new_node

	def find_node(self, id):
		return self.nodes.get(id, None)

	def initialize_tree(self, n):
		for id in range(n):
			self.add_node(id, None)

	def path_to_leaf(self, leaf_id):
		path = []
		current = self.find_node(leaf_id)
		while current is not None:
			path.append(current.id)
			current = current.parent
		return path[::-1]

	def get_node_ids_of_level(self, level_index):
		first_index_in_level = (2 ** level_index) - 1
		return list(range(first_index_in_level, (2 * first_index_in_level) + 1))

	def get_path_to_leaf(self, leaf_index: int, tree_height: int) -> List[int]:
		"""
		get list of indices of nodes from root to given leaf
		"""
		path = []
		curr_node = leaf_index
		for i in range(tree_height + 1):
			path.append(curr_node)
			curr_node = math.floor((curr_node - 1) / 2)

		return path[::-1]

	def __repr__(self):
		return f"BinaryTree(root={self.root})"

	def print_tree(self):
		if not self.root:
			print("Tree is empty.")
			return

		self._print_tree_recursive(self.root, 0, "Root")

	def _print_tree_recursive(self, node, level, position):
		if node:
			indent = "    " * level
			print(f"{indent}|- {position}: {node.data}")
			self._print_tree_recursive(node.left, level + 1, "Left")
			self._print_tree_recursive(node.right, level + 1, "Right")
