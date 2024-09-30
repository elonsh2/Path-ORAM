import hashlib
from math import ceil, log2
import random
from typing import Tuple, List
from Crypto import Random
from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
from Server import Server

DATA_SIZE = 4
KEY_SIZE = 32
NONCE_SIZE = 8
DUMMY_DATA = '0000'
DUMMY_ID = 'x'
ROOT_ID = 0


class Client:
    """
    enables storage, retrieval, and deletion of data from the server storage while ensuring the server remains unaware
    of the data content and access pattern. The client also supports encryption, decryption, and authentication of data.
    """

    def __init__(self, num_of_files: int, server: Server):
        """
        :param num_of_files: Number of files that the server needs to support
        :param server: Server object
        """
        self.max_files = num_of_files
        self.tree_height = max(0, ceil(log2(num_of_files)) - 1)
        num_of_leaves = 2 ** self.tree_height
        self.tree_size = (2 * num_of_leaves) - 1
        self.bucket_size = 4  # stated in the paper, should be enough to prevent overflow
        self.leaves_ids = list(range(num_of_leaves - 1, self.tree_size))
        self.stash = dict()
        self.position_map = dict()
        self.secret_key = get_random_bytes(KEY_SIZE)
        self.init_tree(server)

    def init_tree(self, server: Server) -> None:
        """
        Initialize the tree structure by writing encrypted dummy data to the server.
        :param server: Instance of the Server class where data will be written.
        """
        for bucket_id in range(self.tree_size):
            encrypted_bucket = [self.encrypt_data(DUMMY_ID, DUMMY_DATA) for _ in range(self.bucket_size)]
            server.write_bucket_by_index(bucket_id, encrypted_bucket)

    def read_path(self, leaf_index: int, server: Server) -> Tuple[List[List[str]], List[int]]:
        """
        Read the path from the root to a specified leaf index from the server.
        :param leaf_index: Index of the leaf node whose path to read.
        :param server: Instance of the Server class containing the tree structure.
        :return: Tuple containing the data (buckets) along the path and their corresponding ids.
        """
        path_ids = server.tree.get_path_to_leaf(leaf_index, self.tree_height)
        path_buckets = server.get_buckets_by_ids(path_ids)
        return path_buckets, path_ids

    def get_next_id_in_path_to_leaf(self, data_id: int, curr_bucket_id: int, server) -> int:
        """
        Determine the next node index on the path to a leaf node in the tree structure.

        :param data_id: ID of the data for which the path to a leaf node is being determined.
        :param curr_bucket_id: Current index of the bucket in the tree traversal path.
        :param server: Instance of the Server class containing the tree structure.
        :return: Index of the next node in the path to the leaf node.
        """
        bucket = server.tree.find_node(curr_bucket_id)

        if data_id == DUMMY_ID:
            # If the data ID is a dummy ID, return one of the bucket's children
            left_child_index = bucket.get_left_index()
            right_child_index = bucket.get_right_index()
            return random.choice([left_child_index, right_child_index])

        # If the data ID is not a dummy ID, return its leaf index
        leaf_id = self.position_map[data_id]

        if leaf_id == curr_bucket_id:
            # If the current bucket index is the leaf node, return the leaf index itself
            return leaf_id

        # Get the path ids from the current bucket index to the leaf index
        path_ids = server.tree.get_path_to_leaf(leaf_id, self.tree_height)

        # Find the current index in the path list
        curr_index_in_path_list = path_ids.index(curr_bucket_id)

        # Return the index of the next node in the path to the leaf node
        return path_ids[curr_index_in_path_list + 1]

    def insert_data_to_bucket(self, encrypted_data, bucket, bucket_id: int, server: Server) -> None:
        """
        Replace the first dummy data in the bucket with the provided encrypted data.
        Decrypt and re-encrypt all data blocks in the bucket and write them back to the server.
        :param encrypted_data: Encrypted data to insert into the bucket.
        :param bucket: Current encrypted data blocks in the bucket.
        :param bucket_id: Index of the bucket in the server storage.
        :param server: Instance of the Server class containing the storage.
        """
        new_bucket = []
        replaced_with_dummy = False
        for encrypted_block in bucket:
            curr_data_id, curr_data = self.decrypt_data(encrypted_block)

            if (not replaced_with_dummy) and (curr_data_id == DUMMY_ID):
                # Replace the first dummy data found with the encrypted data
                new_bucket.append(encrypted_data)
                replaced_with_dummy = True
            else:
                # Re-encrypt the existing data and add it to the new_bucket
                re_encrypted_data = self.encrypt_data(curr_data_id, curr_data)
                new_bucket.append(re_encrypted_data)

        # Write the re-encrypted bucket with added data back to the server
        server.write_bucket_by_index(bucket_id, new_bucket)

    def remove_data_from_bucket(self, target_data_id: int, bucket, bucket_index: int, server: Server,
                                should_remove: bool):
        """
        Remove data associated with the specified data ID from the bucket.
        Decrypt and re-encrypt all data blocks in the bucket, replacing the removed data with dummy data.
        Write the modified bucket back to the server.

        :param target_data_id: ID of the data to be removed from the bucket.
        :param bucket: List of encrypted data blocks representing the current contents of the bucket.
        :param bucket_index: Index of the bucket in the server storage.
        :param server: Instance of the Server class containing the storage.
        :param should_remove: Boolean indicating whether to continue removing data (used internally).
        :return: The removed data (if found) associated with the specified data ID.
        """
        removed_data = None
        updated_bucket = []
        for encrypted_block in bucket:
            data_id, data = self.decrypt_data(encrypted_block)
            if should_remove and (data_id == target_data_id):
                # Found the data to remove, replace it with dummy data
                removed_data = data
                re_encrypted_block = self.encrypt_data(DUMMY_ID, DUMMY_DATA)
            else:
                # Re-encrypt the existing data and add it to the updated bucket
                re_encrypted_block = self.encrypt_data(data_id, data)
            updated_bucket.append(re_encrypted_block)  # Add encrypted block to the updated bucket
        # Write the fully re-encrypted bucket back to the server
        server.write_bucket_by_index(bucket_index, updated_bucket)
        return removed_data

    def is_bucket_full(self, bucket_id: int, server: Server) -> bool:
        """
        Check if a bucket in the server storage is full of real data (non-dummy data).
        :param bucket_id: Index of the bucket to check.
        :param server: Instance of the Server class containing the storage.
        :return: True if the bucket is full of real data, False otherwise.
        """
        bucket = server.get_bucket_by_index(bucket_id)
        for encrypted_block in bucket:
            curr_data_id, curr_data = self.decrypt_data(encrypted_block)
            if curr_data_id == DUMMY_ID:
                # If any block in the bucket contains dummy data, the bucket is not full
                return False
        # If no blocks contain dummy data, the bucket is considered full
        return True

    def prevent_overflow(self, server: Server):
        """
        Prevent overflows in the tree according to the algorithm in the paper.
        This method iterates through each level of the tree (excluding leaves) and
        selects random buckets to push data down to prevent overflow.
        :param server: Instance of the Server class containing the storage.
        """
        for level in range(self.tree_height):  # Iterate through each level except leaves
            if level == ROOT_ID:  # Root level only has one bucket
                chosen_bucket_ids = [ROOT_ID]
            else:  # Other levels have at least two buckets
                level_ids = server.tree.get_node_ids_of_level(level)
                chosen_bucket_ids = random.sample(level_ids, 2)  # Randomly choose two buckets from the current level

            chosen_buckets = server.get_buckets_by_ids(chosen_bucket_ids)

            for bucket_id, bucket in zip(chosen_bucket_ids, chosen_buckets):  # For each chosen bucket
                index_to_push_down = random.randint(0, self.bucket_size - 1)  # Choose one data block to push down
                new_bucket = []
                data_to_push_down = None
                data_id_to_push_down = None

                for index, encrypted_block in enumerate(bucket):  # Iterate through each data block in the bucket
                    data_id, data = self.decrypt_data(encrypted_block)

                    if index == index_to_push_down:  # The data block to push down, replace with dummy
                        data_to_push_down = data
                        data_id_to_push_down = data_id
                        re_encrypted_block = self.encrypt_data(DUMMY_ID, DUMMY_DATA)
                    else:  # Not the data block to push down
                        re_encrypted_block = self.encrypt_data(data_id, data)

                    new_bucket.append(re_encrypted_block)

                # Write the re-encrypted bucket back to the server
                server.write_bucket_by_index(bucket_id, new_bucket)

                if data_to_push_down is not None:
                    # Push the data down as deep as possible in the tree
                    self.push_data_down_as_deep_as_possible(server, bucket_id, data_id_to_push_down, data_to_push_down)

    def push_data_down_as_deep_as_possible(self, server: Server, current_index: int, data_id: int, data) -> None:
        """
        Pushes data down the tree as deep as possible without causing overflow.

        This function encrypts the given data and attempts to move it from the current node
        down to the deepest node in the tree. If a non-full bucket is found during the process,
        the data is inserted into that bucket.

        :param server: Instance of the Server class that manages the storage.
        :param current_index: Index of the current node in the tree where the push starts.
        :param data_id: ID of the data to be pushed down.
        :param data: The data to be pushed down.
        """
        # Encrypt the data to be pushed down
        encrypted_push_down = self.encrypt_data(data_id, data)

        # Initialize path to keep track of nodes visited during traversal
        path = []
        current_node_index = current_index

        # Traverse down the tree until a leaf node is reached
        while True:
            current_node = server.get_node_by_index(current_node_index)
            left_child_index = current_node.get_left_index()
            right_child_index = current_node.get_right_index()

            # If at a leaf node, break the loop
            if left_child_index is None or right_child_index is None:
                break

            # Record the current node in the path
            path.append(current_node_index)

            # Determine the next node to visit in the path to the leaf
            next_node_index_to_leaf = self.get_next_id_in_path_to_leaf(data_id, current_node_index, server)

            # Move to the left or right child based on the next node index
            if next_node_index_to_leaf == left_child_index:
                current_node_index = left_child_index
            else:
                current_node_index = right_child_index

        # Add the deepest node to the path
        path.append(current_node_index)

        # Backtrack from the deepest node to find a non-full bucket
        while path:
            node_to_write = path.pop()

            # Check if the bucket at the current node is not full
            if not self.is_bucket_full(node_to_write, server):
                # Retrieve the bucket to write the data to
                bucket_to_write = server.get_bucket_by_index(node_to_write)

                # Insert the encrypted data into the bucket
                self.insert_data_to_bucket(encrypted_push_down, bucket_to_write, node_to_write, server)
                return

    ############ Encryption & Decryption ##############

    def encrypt_data(self, data_id: int | str, data: str) -> str | bytes:
        """
        Encrypts the given data with the specified data ID. Using AES with CTR mode.
        :param data_id: The identifier for the data to be encrypted.
        :param data: The actual data to be encrypted.
        :return: The encrypted data as a combination of nonce and ciphertext, or plain concatenation if encryption is not used.
        """
        # Generate a random nonce
        nonce = Random.get_random_bytes(8)
        counter = Counter.new(64, nonce)
        cipher = AES.new(self.secret_key, AES.MODE_CTR, counter=counter)

        # Convert the data (str) to bytes
        data_in_bytes = str(str(data_id) + data).encode()

        # Encrypt the data
        cipher_in_bytes = cipher.encrypt(data_in_bytes)
        # Calculate HMAC of the ciphertext
        hmac_key = hashlib.sha256(self.secret_key).digest()
        hmac = HMAC.new(hmac_key, digestmod=SHA256)
        hmac.update(nonce + cipher_in_bytes)
        tag = hmac.digest()

        # Return the combination of nonce and ciphertext
        return nonce + cipher_in_bytes + tag

    def decrypt_data(self, data: str | bytes) -> Tuple[int | str, str]:
        """
        Decrypts the given encrypted data.

        :param data: The encrypted data to be decrypted. This can be a string or bytes.
        :return: A tuple containing the data ID (or identifier) and the actual data.
        """
        # Decryption logic when encryption is used
        nonce_in_bytes, ciphertext_in_bytes, tag = data[:NONCE_SIZE], data[NONCE_SIZE:-KEY_SIZE], data[-KEY_SIZE:]
        # Verify HMAC of the ciphertext
        hmac_key = hashlib.sha256(self.secret_key).digest()
        hmac = HMAC.new(hmac_key, digestmod=SHA256)
        hmac.update(nonce_in_bytes + ciphertext_in_bytes)
        # The server won't be unable to trick the client into accepting outdated data
        try:
            hmac.verify(tag)
        except ValueError:
            raise ValueError("Decryption failed: authentication failed")

        counter = Counter.new(64, nonce_in_bytes)
        cipher = AES.new(self.secret_key, AES.MODE_CTR, counter=counter)

        try:
            # Decrypt the ciphertext
            plaintext = bytes.decode(cipher.decrypt(ciphertext_in_bytes))

            # Extract the ID and actual data
            if plaintext[:-DATA_SIZE].isnumeric():  # If ID is a number, it's not dummy data
                data_id = int(plaintext[:-DATA_SIZE])
                data = plaintext[-DATA_SIZE:]
            else:  # If ID is not a number, it's dummy data
                data_id = plaintext[:-DATA_SIZE]
                data = plaintext[-DATA_SIZE:]
            return data_id, data
        # The server won't be unable to trick the client into accepting corrupt data
        except (ValueError, KeyError) as e:
            print("Incorrect decryption:", e)
            raise "decryption failed. there was a problem."

    ################ API  ##############

    def store_data(self, server: Server, data_id: int, data: str) -> bool:
        """
        Store the data in the root bucket. Decrypt the root bucket and locate a dummy entry to substitute with the given data.
        Assign a new random leaf to the data and update the position map.
        Invoke prevent_overflow() to prevent the root from filling up with real data.
        :param server: Server object
        :param data_id: ID to find in the server
        :param data: None if called as API call, new data if called from store_data API call
        :return: requested data.
        """

        if data_id in self.position_map:
            self.retrieve_data(server, data_id, data)
            return True
        if not data or len(data) != DATA_SIZE:
            print(f'Error: data must be string of {DATA_SIZE} characters')
            return False
        if self.is_bucket_full(ROOT_ID, server):
            print("Root is full, probably because tree is overflowing. Storing data in stash")
            self.stash[data_id] = data
            return True

        encrypted_data = self.encrypt_data(data_id, data)
        root_bucket = server.get_bucket_by_index(ROOT_ID)
        self.insert_data_to_bucket(encrypted_data, root_bucket, ROOT_ID, server)

        # Allocate a new random leaf for the data and store it in the position map.
        self.position_map[data_id] = random.choice(self.leaves_ids)
        # Shift data blocks downwards in the tree structure to prevent overflows.
        self.prevent_overflow(server)
        return True

    def retrieve_data(self, server: Server, data_id: int, data=None) -> str | None:
        """
        Retrieve the data by its ID. Search for the correct path from the root to the leaf for the given data using its ID.
        Call store_data() to write the retrieved data back to the root.
        :param server: Server object
        :param data_id: ID to find in the server
        :param data: None if called as API call, new data if called from store_data API call
        :return: Requested data.
        """
        # first search in stash
        if data_id in self.stash:
            searched_data = self.stash[data_id]
        elif data_id not in self.position_map:
            return None
        else:  # data is in tree
            # the data is in the path from root to leaf_of_data
            leaf_of_data = self.position_map[data_id]
            path_buckets, path_ids = self.read_path(leaf_of_data, server)
            # Traverse the path from the root to the leaf, searching for the desired data along the way.
            searched_data = None
            for bucket_index, bucket in zip(path_ids, path_buckets):
                still_searching = searched_data is None
                removed_data = self.remove_data_from_bucket(data_id, bucket, bucket_index, server, still_searching)
                if still_searching:
                    searched_data = removed_data
            # Since the data is no longer in storage, remove its ID from the position map.
            self.position_map.pop(data_id)
            if data:  # in case we want to replace the data
                searched_data = data
        # store the data after it has been read, in order to shuffle the tree
        self.store_data(server, data_id, searched_data)
        return searched_data

    def delete_data(self, server: Server, data_id: int, data=None) -> None:
        """
        Remove the data corresponding to the given ID and delete the ID from the position_map.
        :param server: Server object
        :param data_id: ID to delete from the server
        :param data: unused
        :return: None
        """
        if data_id in self.stash:  # delete file from stash
            self.stash.pop(data_id)
            return
        if data_id not in self.position_map:
            print('Error: given data_id does not exist in server')
            return
        leaf_of_data = self.position_map[data_id]
        path_buckets, path_ids = self.read_path(leaf_of_data, server)
        # Traverse the path from the root to the leaf, searching for the desired data along the way.
        searched_data = None
        for bucket_index, bucket in zip(path_ids, path_buckets):
            still_searching = searched_data is None
            removed_data = self.remove_data_from_bucket(data_id, bucket, bucket_index, server,
                                                        still_searching)
            if still_searching:
                searched_data = removed_data
        # Since the data is no longer in storage, remove its ID from the position map.
        self.position_map.pop(data_id)
