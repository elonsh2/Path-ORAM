import queue
import threading
from Client import Client
from Server import Server


class DefaultClient:
    def __init__(self, N: int, client: Client, server: Server, request_queue: queue.Queue):
        self.server = server
        self.N = N
        self.client = client
        self.request_queue = request_queue
        self.running = True  # Flag to control the thread
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.running:  # Check the flag to stop the loop
            try:
                operation, index, data = self.request_queue.get(timeout=0.000001)  # needed to avoid busy waiting
                if operation == 'store':
                    self.store_data(index, data)
                elif operation == 'retrieve':
                    self.retrieve_data(index)
                elif operation == 'delete':
                    self.delete_data(index)
                self.request_queue.task_done()
            except queue.Empty:
                continue



    def stop(self):
        self.running = False  # Set the flag to stop the thread
        self.thread.join()  # Wait for the thread to finish

    def store_data(self, index: int, data: str):
        self.client.store_data(self.server, index, data)

    def retrieve_data(self, index: int):
        return self.client.retrieve_data(self.server, index)

    def delete_data(self, index: int):
        self.client.delete_data(self.server, index)

