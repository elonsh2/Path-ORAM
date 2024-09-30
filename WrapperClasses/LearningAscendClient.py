from queue import Queue
import random
import string
from Client import Client
from Server import Server
from timeit import default_timer as timer
from WrapperClasses.AscendClient import AscendClient


class LearningAscendClient(AscendClient):
    def __init__(self, N: int, client: Client, server: Server, request_queue: Queue, result_queue: Queue, mode: string,
                 gui_update_callback):
        self.server = server
        self.N = N
        self.client = client
        self.rate = self.set_rate()
        if mode == 'power':
            self.mode = 'power'
            self.rate *= 5
        elif mode == 'performance':
            self.mode = 'performance'
            self.rate *= 1.3
        super().__init__(N, client, server, request_queue, result_queue, self.rate, gui_update_callback)

    # def run(self):
    #     while self.running:  # Check the flag to stop the loop
    #         start_time = time.time()
    #         try:
    #             operation, index, data = self.request_queue.get(timeout=self.rate)  # Wait for a request with a timeout
    #             elapsed_time = time.time() - start_time
    #             remaining_time = self.rate - elapsed_time
    #             if remaining_time > 0:
    #                 time.sleep(remaining_time)  # Wait for the remainder of the timeout
    #             if operation == 'store':
    #                 self.store_data(index, data)
    #             elif operation == 'retrieve':
    #                 self.retrieve_data(index)
    #             elif operation == 'delete':
    #                 self.delete_data(index)
    #             self.request_queue.task_done()
    #         except Empty:
    #             print('Dummy request was made to the server')
    #             self.dummy_request_count += 1
    #             self.retrieve_data(0)
    #
    # def stop(self):
    #     self.running = False  # Set the flag to stop the thread
    #     self.thread.join()  # Wait for the thread to finish
    #
    # def store_data(self, index: int, data: str):
    #     self.client.store_data(self.server, index, data)
    #
    # def retrieve_data(self, index: int):
    #     return self.client.retrieve_data(self.server, index)
    #
    # def delete_data(self, index: int):
    #     self.client.delete_data(self.server, index)

    def set_rate(self):
        random_strings = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in
                          range(self.N)]
        total_requests = 0
        timer_start = timer()
        for index in range(self.N):
            self.client.store_data(self.server, index, random_strings[index])
            total_requests += 1
        for index in range(self.N):
            self.client.retrieve_data(self.server, index)
            total_requests += 1
        for index in range(self.N):
            self.client.delete_data(self.server, index)
            total_requests += 1
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        return avg_request_time
