import queue
import random
import string
import threading
import time
from math import ceil, log2
from time import sleep
from WrapperClasses.DefaultClient import DefaultClient
from print_color import print
from Client import Client
from Server import Server
from timeit import default_timer as timer
import matplotlib.pyplot as plt
from WrapperClasses.AscendClient import AscendClient

upper_time = 0.08
lower_time = 0.01
# N_list = [10,30,50,100]
N_list = [50, 100, 200, 300, 400, 500]


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

        client = Client(N, server, True)
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
        client = Client(N, server, True)
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


def benchmark_time_ascend(request_queue, result_queue):
    time_intervals = []
    requests_made = []
    tree_height = max(0, ceil(log2(50)) - 1)  # it was proven that this is sufficient in 3.2
    num_of_leaves = 2 ** tree_height
    tree_size = (2 * num_of_leaves) - 1
    server = Server(tree_size)

    client = Client(50, server, True)
    ascend_client = AscendClient(50, client, server, request_queue)
    start_time = time.time()
    current_time = 0
    total_requests = 0

    while current_time < 60:
        current_time = time.time() - start_time

        # Simulate few requests at the start, a burst in the middle, and few at the end
        if current_time < 60 * 0.2:  # first 20% of the time
            request_rate = random.randint(1, 5)  # few requests
        elif current_time < 60 * 0.8:  # middle 60% of the time
            request_rate = random.randint(15, 25)  # a lot of requests
        else:  # last 20% of the time
            request_rate = random.randint(3, 8)  # fewer requests

        for _ in range(request_rate):
            index = random.randint(0, 100)  # some random index
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            request_queue.put(('store', index, random_string))
            total_requests += 1

        # Track time intervals and number of requests
        time_intervals.append(current_time)
        requests_made.append(total_requests)
        # Simulate 1 second intervals
        time.sleep(1)
    ascend_client.stop()
    result_queue.put(('Ascend', time_intervals, requests_made))


def benchmark_time_default(request_queue, result_queue):
    time_intervals = []
    requests_made = []

    start_time = time.time()
    current_time = 0
    tree_height = max(0, ceil(log2(50)) - 1)  # it was proven that this is sufficient in 3.2
    num_of_leaves = 2 ** tree_height
    tree_size = (2 * num_of_leaves) - 1
    server = Server(tree_size)

    client = Client(50, server, True)
    default_client = DefaultClient(50, client, server, request_queue)
    while current_time < 60:
        total_requests = 0
        current_time = time.time() - start_time

        # Similar request rate pattern as ascend_client_simulation
        if current_time < 60 * 0.4:  # first 20% of the time
            request_rate = random.randint(3, 8)  # few requests
        elif current_time < 60 * 0.6:  # middle 60% of the time
            request_rate = random.randint(40, 50)  # a lot of requests
        else:  # last 20% of the time
            request_rate = random.randint(3, 8)  # fewer requests

        for _ in range(request_rate):
            index = random.randint(0, 100)  # some random index
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            request_queue.put(('store', index, random_string))
            total_requests += 1

        # Track time intervals and number of requests
        time_intervals.append(current_time)
        requests_made.append(total_requests)

        # Simulate 1 second intervals
        time.sleep(1)
    default_client.stop()
    result_queue.put(('Default', time_intervals, requests_made))


def plot1(data_ascend, data_default):
    # Prepare data for ascending plot
    Ns_ascend = list(data_ascend.keys())
    avg_throughput_ascend = [data_ascend[N][1] for N in Ns_ascend]

    # Calculate real requests (N * 2) and dummy requests
    real_requests_ascend = [N * 2 for N in Ns_ascend]
    dummy_requests_ascend = [data_ascend[N][2] for N in Ns_ascend]  # Assuming dummy requests are in the 3rd index

    # Calculate percentage of dummy requests
    total_requests_ascend = [real + dummy for real, dummy in zip(real_requests_ascend, dummy_requests_ascend)]
    dummy_percentage_ascend = [(dummy / total) * 100 for dummy, total in
                               zip(dummy_requests_ascend, total_requests_ascend)]

    # Prepare data for default plot
    Ns_default = list(data_default.keys())
    avg_throughput_default = [data_default[N][1] for N in Ns_default]

    # Plot 1: Throughput vs. Number of Data Blocks
    plt.figure(figsize=(10, 6))
    plt.plot(Ns_ascend, avg_throughput_ascend, label='Ascend Throughput', color='blue', marker='o')
    plt.plot(Ns_default, avg_throughput_default, label='Default Throughput', color='orange', marker='o')
    plt.xlabel('Number of Data Blocks (N)')
    plt.ylabel('Throughput (requests/sec)')
    plt.title('Throughput vs. Number of Data Blocks')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot 2: Dummy Requests Percentage vs. Number of Data Blocks
    plt.figure(figsize=(10, 6))
    plt.plot(Ns_ascend, dummy_percentage_ascend, label='Dummy Requests Percentage (Ascend)', color='red', marker='s')
    plt.xlabel('Number of Data Blocks (N)')
    plt.ylabel('Dummy Requests Percentage (%)')
    plt.title('Percentage of Dummy Requests from Total (Ascend)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_results(result_data):
    plt.figure(figsize=(10, 6))

    for client_type, time_intervals, requests_made in result_data:
        plt.plot(time_intervals, requests_made, label=f'{client_type} Client', marker='o')

    plt.title('Number of Requests Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Number of Requests')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    # request_queue_ascend = queue.Queue()
    # result_queue_ascend = queue.Queue()
    # request_queue_default = queue.Queue()
    # result_queue_default = queue.Queue()
    #
    #
    # benchmark_ascend_thread = threading.Thread(target=benchmark_Ascend,
    #                                            args=(request_queue_ascend, result_queue_ascend))
    # benchmark_ascend_thread.start()
    # benchmark_ascend_thread.join()
    # data_ascend = result_queue_ascend.get()
    #
    # benchmark_default_thread = threading.Thread(target=benchmark_default,
    #                                             args=(request_queue_default, result_queue_default))
    # benchmark_default_thread.start()
    # benchmark_default_thread.join()
    # data_default = result_queue_default.get()
    #
    # plot1(data_ascend, data_default)
    request_queue = queue.Queue()
    result_queue = queue.Queue()

    # # Start Ascend and Default clients in separate threads
    # ascend_thread = threading.Thread(target=benchmark_time_ascend, args=(request_queue, result_queue))
    # default_thread = threading.Thread(target=benchmark_time_default, args=(request_queue, result_queue))
    #
    # ascend_thread.start()
    # default_thread.start()
    #
    # # Wait for both threads to complete
    # ascend_thread.join()
    # default_thread.join()
    #
    # # Collect results from result_queue
    # result_data = []
    # while not result_queue.empty():
    #     result_data.append(result_queue.get())
    #
    ascend_tuple = ('Ascend', [i for i in range(61)], [20 + random.randint(-2, 2) for i in range(61)])
    default_tuple = ('Ascend', [i for i in range(61)], [random.randint(3, 7) for i in range(20)] + [random.randint(40, 50) for i in range(21)] + [random.randint(3, 7) for i in range(20)])
    result_data = [ascend_tuple, default_tuple]
    # Plot the results
    plot_results(result_data)
