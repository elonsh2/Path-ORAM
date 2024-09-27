import queue
import random
import string
import threading
from math import ceil, log2
from time import sleep
from WrapperClasses.DefaultClient import DefaultClient
from print_color import print
from Client import Client
from Server import Server
from timeit import default_timer as timer
import matplotlib.pyplot as plt
from WrapperClasses.AscendClient import AscendClient

upper_time = 0.1
lower_time = 0.05
N_list = [50,80,100,200,300,500]


def benchmark_Ascend(request_queue, result_queue):
    data = {}
    print('Ascend Mode:')
    for N in N_list:
        print('--------------------')
        print(f'N = {N}\n')
        tree_height = max(0, ceil(log2(N)) - 1)  # it was proven that this is sufficient in 3.2
        num_of_leaves = 2 ** tree_height
        tree_size = (2 * num_of_leaves) - 1
        server = Server(tree_size)

        client = Client(N, server, False)
        ascend_client = AscendClient(N, client, server, request_queue)
        random_strings = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in
                          range(N)]
        total_requests = 0
        timer_start = timer()
        for index in range(N):
            sleep(random.uniform(lower_time, upper_time))
            request_queue.put(('store', index, random_strings[index]))
            total_requests += 1
        for index in range(N):
            sleep(random.uniform(lower_time, upper_time))
            request_queue.put(('retrieve', index, None))
            total_requests += 1
        request_queue.join()
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        Throughput = total_requests / total_time
        data[N] = (avg_request_time, Throughput, ascend_client.dummy_request_count)
        print(f"Request per second = {Throughput}")
        ascend_client.stop()  # Stop the AscendClient thread after finishing the loop
    print('--------------------')
    result_queue.put(data)


def benchmark_default(request_queue, result_queue):
    data = {}
    print('Default Mode:')
    for N in N_list:
        print('--------------------')
        print(f'N = {N}\n')
        tree_height = max(0, ceil(log2(N)) - 1)  # it was proven that this is sufficient in 3.2
        num_of_leaves = 2 ** tree_height
        tree_size = (2 * num_of_leaves) - 1

        server = Server(tree_size)
        client = Client(N, server, False)
        default_client = DefaultClient(N, client, server, request_queue)
        random_strings = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in
                          range(N)]
        total_requests = 0
        timer_start = timer()
        for index in range(N):
            sleep(random.uniform(lower_time, upper_time))
            request_queue.put(('store', index, random_strings[index]))
            # default_client.store_data(index, random_strings[index])
            total_requests += 1
        for index in range(N):
            sleep(random.uniform(lower_time, upper_time))
            request_queue.put(('retrieve', index, None))
            # default_client.retrieve_data(index)
            total_requests += 1
        request_queue.join()
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        Throughput = total_requests / total_time
        data[N] = (avg_request_time, Throughput)
        print(f"Request per second = {Throughput}")
        default_client.stop()
    print('--------------------')
    result_queue.put(data)


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
    request_queue_ascend = queue.Queue()
    result_queue_ascend = queue.Queue()
    request_queue_default = queue.Queue()
    result_queue_default = queue.Queue()


    benchmark_ascend_thread = threading.Thread(target=benchmark_Ascend,
                                               args=(request_queue_ascend, result_queue_ascend))
    benchmark_ascend_thread.start()
    benchmark_ascend_thread.join()
    data_ascend = result_queue_ascend.get()

    benchmark_default_thread = threading.Thread(target=benchmark_default,
                                                args=(request_queue_default, result_queue_default))
    benchmark_default_thread.start()
    benchmark_default_thread.join()
    data_default = result_queue_default.get()

    plot(data_ascend, data_default)
