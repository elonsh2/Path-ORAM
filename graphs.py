import random
import string
from math import ceil, log2
from print_color import print
from Client import Client
from Server import Server
from timeit import default_timer as timer
import matplotlib.pyplot as plt


def plot_results(throughput_data, latency_data):
    Ns = [data[0] for data in throughput_data]

    # Calculate average throughput and latency
    avg_throughput = [(data[1] + data[2] + data[3]) / 3 for data in throughput_data]
    avg_latency = [(data[1] + data[3] + data[5]) / 3 for data in latency_data]

    plt.figure(figsize=(12, 6))

    # Plot average throughput vs. N
    plt.subplot(1, 2, 1)
    plt.plot(Ns, avg_throughput, label='Average Throughput', marker='o')
    plt.xlabel('Number of Data Blocks (N)')
    plt.xticks(list(range(500, 5500, 500)))  # Set X-axis intervals to 500
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


# Running the test and plotting the results


def test1():
    data = {}
    for N in [4, 10, 50, 100, 300, 500, 700, 1000]:
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
            client.store_data(server, index, random_strings[index])
            total_requests += 1
        for index in range(N):
            r = client.retrieve_data(server, index)
            total_requests += 1
            if r != random_strings[index]:
                print("wrong retrive")
        for index in range(N):
            client.delete_data(server, index)
            total_requests += 1
        timer_end = timer()
        total_time = timer_end - timer_start
        avg_request_time = total_time / total_requests
        Throughput = total_requests / total_time
        data[N] = (avg_request_time, Throughput)
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
    plt.xticks(list(range(0, 1001, 100)))  # Set X-axis intervals to 500
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
    data = test1()
    plot(data)
