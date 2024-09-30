import queue
import threading
from queue import Queue

from Client import Client
from Server import Server


class DefaultClient:
    def __init__(self, N: int, client: Client, server: Server, request_queue: Queue, result_queue: Queue,
                 gui_update_callback):
        self.gui_update_callback = gui_update_callback
        self.server = server
        self.N = N
        self.client = client
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.running = True  # Flag to control the thread
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.running:  # Check the flag to stop the loop
            try:
                operation, index, data = self.request_queue.get(timeout=0.000001)  # needed to avoid busy waiting
                self.gui_print(f'{operation.capitalize()} Request')
                if operation == 'store':
                    self.store_data(index, data)
                elif operation == 'retrieve':
                    self.result_queue.put(self.retrieve_data(index))
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
        
    def gui_print(self, message):
        """Print a message in the GUI."""
        # Add the message and a new line for the next update
        self.gui_update_callback(f"{message}\n")  # Real operation message
