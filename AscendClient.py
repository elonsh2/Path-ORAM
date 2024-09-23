import queue
import random
import string
import threading
import time

from print_color import print
from Client import Client
from Server import Server
from timeit import default_timer as timer


class AscendClient:
    def __init__(self, N: int, client: Client, server: Server, request_queue: queue.Queue):
        self.server = server
        self.N = N
        self.client = client
        self.rate = self.set_rate()
        self.request_queue = request_queue
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while True:
            start_time = time.time()
            try:
                operation, index, data = self.request_queue.get(timeout=self.rate)  # Wait for a request with a timeout
                elapsed_time = time.time() - start_time
                remaining_time = self.rate - elapsed_time
                if remaining_time > 0:
                    time.sleep(remaining_time)  # Wait for the remainder of the timeout
                print(str(int(time.time()))[-2:])
                if operation == 'store':
                    self.store_data(index, data)
                    print(f"Stored data for index {index}: {data}")
                elif operation == 'retrieve':
                    data = self.retrieve_data(index)
                    print(f"Retrieved data for index {index}: {data}")
            except queue.Empty:
                print(str(int(time.time()))[-2:])
                print("Sending dummy retrieve request")

    def store_data(self, index: int, data: str):
        self.client.store_data(self.server, index, data)

    def retrieve_data(self, index: int):
        return self.client.retrieve_data(self.server, index)

    def delete_data(self, index: int):
        self.client.delete_data(self.server, index)

    def set_rate(self):
        random_strings = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in
                          range(self.N)]
        total_requests = 0
        timer_start = timer()
        for index in range(self.N):
            self.client.store_data(self.server, index, random_strings[index])
            total_requests += 1
        for index in range(self.N):
            r = self.client.retrieve_data(self.server, index)
            total_requests += 1
            if r != random_strings[index]:
                print("wrong retrieve")
        for index in range(self.N):
            self.client.delete_data(self.server, index)
            total_requests += 1
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        return avg_request_time
