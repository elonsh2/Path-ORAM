import queue
import random
import string
import threading
import time
from Client import Client
from Server import Server
from timeit import default_timer as timer


class AscendClient:
    def __init__(self, N: int, client: Client, server: Server, request_queue: queue.Queue, rate: int):
        self.server = server
        self.N = N
        self.client = client
        self.rate = rate  # Rate of requests per second
        self.request_queue = request_queue
        self.dummy_request_count = 0
        self.running = True  # Flag to control the thread
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.running:  # Check the flag to stop the loop
            start_time = time.time()
            try:
                operation, index, data = self.request_queue.get(timeout=self.rate)  # Wait for a request with a timeout
                elapsed_time = time.time() - start_time
                remaining_time = self.rate - elapsed_time
                if remaining_time > 0:
                    time.sleep(remaining_time)  # Wait for the remainder of the timeout
                if operation == 'store':
                    self.store_data(index, data)
                elif operation == 'retrieve':
                    self.retrieve_data(index)
                elif operation == 'delete':
                    self.delete_data(index)
                self.request_queue.task_done()
            except queue.Empty:
                # print('Dummy request')
                self.dummy_request_count+=1
                self.retrieve_data(0)

    def stop(self):
        self.running = False  # Set the flag to stop the thread
        self.thread.join()  # Wait for the thread to finish

    def store_data(self, index: int, data: str):
        self.client.store_data(self.server, index, data)

    def retrieve_data(self, index: int):
        return self.client.retrieve_data(self.server, index)

    def delete_data(self, index: int):
        self.client.delete_data(self.server, index)
