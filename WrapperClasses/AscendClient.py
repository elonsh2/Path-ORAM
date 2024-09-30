import threading
import time
from Client import Client
from Server import Server
from queue import Queue, Empty

from WrapperClasses.DefaultClient import DefaultClient


class AscendClient(DefaultClient):
    def __init__(self, N: int, client: Client, server: Server, request_queue: Queue, result_queue: Queue, rate: float,
                 gui_update_callback):
        self.rate = rate  # Rate of requests per second
        print(f'Running client with rate: {1 / self.rate} requests per second')
        input('Press Enter to start client')
        self.dummy_request_count = 0
        self.last_dummy_count = 0  # Track dummy requests since the last real operation
        super().__init__(N, client, server, request_queue, result_queue, gui_update_callback)
        self.schedule_dummy_update()

    def run(self):
        while self.running:  # Check the flag to stop the loop
            start_time = time.time()
            try:
                operation, index, data = self.request_queue.get(timeout=self.rate)  # Wait for a request with a timeout
                elapsed_time = time.time() - start_time
                remaining_time = self.rate - elapsed_time
                if remaining_time > 0:
                    time.sleep(remaining_time)  # Wait for the remainder of the timeout
                self.gui_print(f'{operation.capitalize()} Request')
                if operation == 'store':
                    self.store_data(index, data)
                elif operation == 'retrieve':
                    self.result_queue.put(self.retrieve_data(index))
                elif operation == 'delete':
                    self.delete_data(index)
                # After a real operation, print the number of dummy requests made
                self.last_dummy_count = self.dummy_request_count
                self.dummy_request_count = 0  # Reset dummy count after printing
                # self.print_dummy_count()
                self.request_queue.task_done()
            except Empty:
                self.dummy_request_count += 1
                self.retrieve_data(0)


    def print_dummy_count(self):
        """Print the number of dummy requests since the last real operation."""
        if self.dummy_request_count > 0:
            self.gui_update_callback(f"Dummy requests made: {self.dummy_request_count}")
            self.last_dummy_count = self.dummy_request_count
            self.dummy_request_count = 0  # Reset dummy count after printing

    def gui_print(self, message):
        """Print a message in the GUI."""
        # Add the message and a new line for the next update
        self.gui_update_callback(f"{message}\n")  # Real operation message
        self.gui_update_callback(f'Dummy requests made: {self.dummy_request_count}\n')  # Initial dummy count

    def schedule_dummy_update(self):
        """Schedule the dummy request count to be updated every second in the GUI."""
        if self.gui_update_callback:
            # Only update the dummy request line if dummy requests are accumulating
            if self.dummy_request_count != self.last_dummy_count:
                self.gui_update_callback(f"Dummy requests made: {self.dummy_request_count}\n")
        # Schedule this method to run again after 1000 ms (1 second)
        threading.Timer(1.0, self.schedule_dummy_update).start()


