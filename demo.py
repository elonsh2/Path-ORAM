import random
from math import ceil, log2
from print_color import print
from Client import Client
from Server import Server

STORE = '1'
RETRIEVE = '2'
DELETE = '3'
PRINT = '4'
EXIT = '0'


def demo1():
	print('Do you want to encrypt the data? Running without encryption is better for demonstration.')
	is_encryption = encrypt('Choose 1 for encryption, 0 for not: ')
	N = get_positive_integer('Enter number of data blocks (positive integer): ')
	print(f'Number of data blocks (N): {N}')

	tree_height = max(0, ceil(log2(N)) - 1)
	num_of_leaves = 2 ** tree_height
	tree_size = (2 * num_of_leaves) - 1
	server = Server(tree_size)
	client = Client(N, server, bool(is_encryption))

	while True:
		request = input('\nChoose operation number: (1)store | (2)retrieve | (3)delete | (4)print | (0)exit\n')

		if request == STORE:
			handle_store(client, server)
		elif request == RETRIEVE:
			handle_retrieve(client, server)
		elif request == DELETE:
			handle_delete(client, server)
		elif request == PRINT:
			handle_print_tree(server)
		elif request == EXIT:
			print('\nExiting')
			break
		else:
			print('Invalid option. Please choose from: 1/2/3/0', color='red')


def encrypt(prompt):
	while True:
		value = input(prompt)
		if value.isdigit() and int(value) in [0, 1]:
			return int(value)
		print('Please enter 0 or 1.', color='red')


def get_positive_integer(prompt: str) -> int:
	while True:
		value = input(prompt)
		if value.isdigit() and int(value) > 0:
			return int(value)
		print('Please enter a positive integer.', color='red')


def get_data_id_from_user() -> int:
	data_id = input('Insert data id (must be integer): ')
	while not data_id.isdigit():
		data_id = input('data id must be integer. choose again: ')
	return int(data_id)


def handle_store(client, server):
	print('\n--- STORE ---', color='blue')
	data_id = get_data_id_from_user()
	data = input('Insert data (string of 4 characters): ')
	client.store_data(server, data_id, data)
	print('Store operation completed.', color='green')


def handle_retrieve(client, server):
	print('\n--- RETRIEVE ---', color='blue')
	data_id = get_data_id_from_user()
	data = client.retrieve_data(server, data_id)
	if data:
		print(f'Requested data: {data}', color='magenta')
	else:
		print('Requested ID not in server storage.', color='red')
	print('Retrieve operation completed.', color='green')


def handle_delete(client, server):
	print('\n--- DELETE ---', color='blue')
	data_id = get_data_id_from_user()
	client.delete_data(server, data_id)
	print('Delete operation completed.', color='green')


def handle_print_tree(server):
	server.tree.print_tree()


def demo2():
	error = 0
	num_of_tests = random.randint(5, 50)
	print(f"Number of tests to run: {num_of_tests}")
	print("Starting tests...")

	for i in range(num_of_tests):
		print(f"Test num: {i}")
		num_of_blocks = random.randint(2, 16)
		print(f"Number of blocks chosen: {num_of_blocks}")
		tree_height = max(0, ceil(log2(num_of_blocks)) - 1)
		num_of_leaves = 2 ** tree_height
		tree_size = (2 * num_of_leaves) - 1
		server = Server(tree_size=tree_size)
		client = Client(num_of_files=num_of_blocks, server=server)
		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)

			if data is not None:
				print("FAIL")
				print(f"Block {i}: {data}")
				print(f"Supposed to be: None")
				error = 1

		# Write data to blocks
		for i in range(num_of_blocks):
			client.store_data(server, i, f"dat{i:X}")

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)
			if data != f"dat{i:X}":
				print("FAIL")
				print(f"Block {i}: {data}")
				print(f"Supposed to be: dat{i:X}\n")
				error = 1

		# Update a block and read it back
		for i in range(num_of_blocks):
			client.store_data(server, i, f"uda{i:X}")

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)
			if data != f"uda{i:X}":
				print("FAIL")
				print(f"Block {i}: {data}")
				print(f"Supposed to be: uda{i:X}\n")
				error = 1

		# Remove a block
		for i in range(num_of_blocks):
			client.delete_data(server, i)

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)
			if data is not None:
				print("FAIL")
				print(f"Block {i}: {data}")
				print(f"Supposed to be: \"NULL\"\n")
				error = 1

		# Update a block and read it back
		for i in range(num_of_blocks):
			client.store_data(server, i, f"udb{i:X}")

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)
			if data != f"udb{i:X}":
				print("FAIL")
				print(f"Block {i}: {data}")
				print(f"Supposed to be: udb{i:X}\n")
				error = 1

		# Update a block and read it back
		for i in range(num_of_blocks):
			if i % 2:
				client.store_data(server, i, f"udc{i:X}")
			else:
				client.store_data(server, i, f"udd{i:X}")

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)
			if i % 2:
				if data != f"udc{i:X}":
					print("FAIL")
					print(f"Block {i}: {data}")
					print(f"Supposed to be: udc{i:X}\n")
					error = 1
			else:
				if data != f"udd{i:X}":
					print("FAIL")
					print(f"Block {i}: {data}")
					print(f"Supposed to be: udd{i:X}\n")
					error = 1

		# Remove a block
		for i in range(num_of_blocks):
			if i % 2:
				client.delete_data(server, i)

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i)
			if i % 2:
				if data is not None:
					print("FAIL")
					print(f"Block {i}: {data}")
					print(f"Supposed to be: \"NULL\"\n")
					error = 1
			else:
				if data != f"udd{i:X}":
					print("FAIL")
					print(f"Block {i}: {data}")
					print(f"Supposed to be: udd{i:X}\n")
					error = 1

		# Remove a block
		for i in range(num_of_blocks):
			if i % 2 == 0:
				client.delete_data(server, i)

		# Update a block and read it back
		for i in range(num_of_blocks):
			client.store_data(server, i, f"ude{i:X}")

		# Access data from blocks
		for i in range(num_of_blocks):
			data = client.retrieve_data(server, i, "")
			if data != f"ude{i:X}":
				print("FAIL")
				print(f"Block {i}: {data}")
				print(f"Supposed to be: ude{i:X}\n")
				error = 1

		# Accessing a non-existent block (beyond initial blocks)
		data = client.retrieve_data(server, num_of_blocks + 1)
		if data is not None:
			print("FAIL")
			print(f"Block {num_of_blocks + 1}: {data}")
			print(f"Supposed to be: None\n")
			error = 1

	if error == 0:
		print("All " + str(num_of_tests) + " tests PASSED")
	else:
		print("Some tests FAILED")
