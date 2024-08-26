from typing import List
from BinaryTree import BinaryTree


class Server:
    """
    Manages storage operations, including adding and retrieving data buckets.
    """

    def __init__(self, tree_size: int):
        self.tree = BinaryTree()
        self.tree.initialize_tree(tree_size)

    def get_node_by_index(self, index: int) -> BinaryTree.TreeNode:
        """
        Retrieve a node from the tree structure by its index.
        :param index: Index of the node to retrieve.
        :return: The node found at the specified index.
        """
        try:
            return self.tree.find_node(index)
        except IndexError as e:
            print(f"Error: {e}")

    def get_bucket_by_index(self, index: int) -> List[str]:
        """
        Retrieve the data (bucket) associated with a node from the tree structure by its index.

        :param index: Index of the node whose data (bucket) is to be retrieved.
        :return: The data (bucket) found at the specified node index.
        """
        try:
            return self.get_node_by_index(index).data
        except IndexError as e:
            print(f"Error: {e}")

    def get_buckets_by_ids(self, ids_list: List[int]) -> List[List[str]]:
        """
        Retrieve the data (buckets) associated with nodes from the tree structure based on a list of indices.

        :param ids_list: List of indices of nodes whose data (buckets) are to be retrieved.
        :return: List of data (buckets) found at the specified node indices.
        """
        return [self.get_bucket_by_index(index) for index in ids_list]

    def write_bucket_by_index(self, index: int, bucket: List[str]) -> None:
        """
        Write a data (bucket) to a node in the tree structure based on the provided index.

        :param index: Index of the node where the data (bucket) will be written.
        :param bucket: Data (bucket) to be written to the node.
        """
        node = self.tree.find_node(index)
        node.data = bucket
