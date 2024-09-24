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
N_list = [10,20,30,50,80,100]

def benchmark_Ascend(request_queue, result_queue):
    data = {}
    for N in N_list:
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
            sleep(0.02)
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
        data[N] = (avg_request_time, Throughput, ascend_client.dummy_request_count)
        print(f"N = {N}, avg_request_time = {avg_request_time}, Throughput = {Throughput}")
        ascend_client.stop()  # Stop the AscendClient thread after finishing the loop

    result_queue.put(data)



def benchmark_default():
    data = {}
    for N in N_list:
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


def plot(data_ascend, data_default):
    Ns_ascend = list(data_ascend.keys())
    avg_throughput_ascend = [data_ascend[N][1] for N in Ns_ascend]

    # Calculate real requests (N * 2) and dummy requests
    real_requests_ascend = [N * 2 for N in Ns_ascend]
    dummy_requests_ascend = [data_ascend[N][2] for N in Ns_ascend]  # Assuming dummy requests are in the 3rd index

    # Get default data
    Ns_default = list(data_default.keys())
    avg_throughput_default = [data_default[N][1] for N in Ns_default]

    # Create a figure with two subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 12))

    # Plot for Throughput vs. Number of Data Blocks
    axs[0].plot(Ns_ascend, avg_throughput_ascend, label='Ascend Throughput', color='blue', marker='o')
    axs[0].plot(Ns_default, avg_throughput_default, label='Default Throughput', color='orange', marker='o')
    axs[0].set_xlabel('Number of Data Blocks (N)')
    axs[0].set_ylabel('Throughput (requests/sec)')
    axs[0].set_title('Throughput vs. Number of Data Blocks')
    axs[0].legend()
    axs[0].grid(True)

    # Plot for Real Requests vs. Dummy Requests
    axs[1].plot(Ns_ascend, real_requests_ascend, label='Real Requests (Ascend)', color='green', marker='x')
    axs[1].plot(Ns_ascend, dummy_requests_ascend, label='Dummy Requests (Ascend)', color='red', marker='s')
    axs[1].set_xlabel('Number of Data Blocks (N)')
    axs[1].set_ylabel('Number of Requests')
    axs[1].set_title('Real vs. Dummy Requests (Ascend)')
    axs[1].legend()
    axs[1].grid(True)

    # Adjust layout and show the plots
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    request_queue = queue.Queue()
    result_queue = queue.Queue()
    shared_data = {'empty_count': 0}  # Shared variable for counting empty occurrences
    lock = threading.Lock()  # Lock for thread-safe access

    benchmark_thread = threading.Thread(target=benchmark_Ascend, args=(request_queue, result_queue))
    benchmark_thread.start()
    benchmark_thread.join()
    data_ascend = result_queue.get()
    # print(f"Number of times queue was empty: {data_ascend[2]}")

    data_default = benchmark_default()
    plot(data_ascend, data_default)
