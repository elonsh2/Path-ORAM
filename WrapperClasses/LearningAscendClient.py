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
