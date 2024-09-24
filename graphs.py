import queue
import random
import string
import sys
import threading
from math import ceil, log2
from time import sleep

from print_color import print
from Client import Client
from Server import Server
from timeit import default_timer as timer
import matplotlib.pyplot as plt
from AscendClient import AscendClient

upper_time = 0.1
lower_time = 0.002

def benchmark_Ascend(request_queue):
    data = {}
    for N in [100]:
        print('--------------------')
        print(f'N = {N}\n')
        tree_height = max(0, ceil(log2(N)) - 1)  # it was proven that this is sufficient in 3.2
        num_of_leaves = 2 ** tree_height
        tree_size = (2 * num_of_leaves) - 1
        server = Server(tree_size)

        client = Client(N, server, True)
        ascend_client = AscendClient(N, client, server, request_queue)
        random_strings = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in
                          range(N)]
        total_requests = 0
        timer_start = timer()
        for index in range(N):
            # sleep(2)
            request_queue.put(('store',index, random_strings[index]))
            total_requests += 1
        for index in range(N):
            # sleep(2)
            request_queue.put(('retrieve',index, None))
            total_requests += 1
        while not request_queue.empty():
            sleep(0.01)
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        Throughput = total_requests / total_time
        data[N] = (avg_request_time, Throughput)
        print(f"N = {N}, avg_request_time = {avg_request_time}, Throughput = {Throughput}")
        ascend_client.stop()  # Stop the AscendClient thread after finishing the loop
    plot(data)



def benchmark_default():
    data = {}
    for N in [100]:
        print('--------------------')
        print(f'N = {N}\n')
        tree_height = max(0, ceil(log2(N)) - 1)  # it was proven that this is sufficient in 3.2
        num_of_leaves = 2 ** tree_height
        tree_size = (2 * num_of_leaves) - 1

        server = Server(tree_size)
        client = Client(N, server, True)
        random_strings = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in
                          range(N)]
        total_requests = 0
        timer_start = timer()
        for index in range(N):
            # sleep(0.05)
            client.store_data(server, index, random_strings[index])
            total_requests += 1
        for index in range(N):
            # sleep(0.05)
            client.retrieve_data(server, index)
            total_requests += 1
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        Throughput = total_requests / total_time
        data[N] = (avg_request_time, Throughput)
        print(f"N = {N}, avg_request_time = {avg_request_time}, Throughput = {Throughput}")
    return data


def plot(data):
    Ns = list(data.keys())
    avg_throughput = [data[N][1] for N in Ns]
    avg_latency = [data[N][0] for N in Ns]
    plt.figure(figsize=(12, 6))

    # Plot average throughput vs. N
    plt.subplot(1, 2, 1)
    plt.plot(Ns, avg_throughput, label='Average Throughput', marker='o')
    plt.xlabel('Number of Data Blocks (N)')
    # plt.xticks(list(range(0, max(Ns)+1, 100)))  # Set X-axis intervals to 500
    plt.ylabel('Throughput (requests/sec)')
    plt.title('Average Throughput vs. N')
    plt.legend()
    plt.grid(True)
    # Plot average latency vs. throughput
    plt.subplot(1, 2, 2)
    plt.plot(avg_throughput, avg_latency, label='Average Latency', marker='o')
    plt.xlabel('Throughput (requests/sec)')
    plt.ylabel('Latency (sec)')
    plt.title('Average Latency vs. Throughput')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    request_queue = queue.Queue()
    benchmark_thread = threading.Thread(target=benchmark_Ascend, args=(request_queue,))
    benchmark_thread.start()
    benchmark_thread.join()

    plot(benchmark_default())
