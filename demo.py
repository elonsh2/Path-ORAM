import queue
import random
import threading
from math import ceil, log2
from print_color import print
from Client import Client
from Server import Server
from WrapperClasses.DefaultClient import DefaultClient
from WrapperClasses.AscendClient import AscendClient
from WrapperClasses.LearningAscendClient import LearningAscendClient
import tkinter as tk

N = 50
STORE = '1'
RETRIEVE = '2'
DELETE = '3'
EXIT = '0'


class Demo:
    def __init__(self, mode):
        def gui_update(message):
            """Callback to update the Tkinter text widget with a message."""
            if "Dummy requests" in message:
                text_widget.delete("end-2l","end-1l")  # Delete the last line
                text_widget.insert(tk.END, message)  # Scroll to the end of the text widget
            else:
                text_widget.insert(tk.END, message + '\n')
                text_widget.see(tk.END)  # Scroll to the end of the text widget


        self.root = tk.Tk()  # Save root as an instance variable
        self.root.title("Client Log")

        # Create a text widget to show the logs
        text_widget = tk.Text(self.root, height=20, width=50)
        text_widget.pack()

        self.mode = mode
        self.N = N
        tree_height = max(0, ceil(log2(N)) - 1)
        num_of_leaves = 2 ** tree_height
        tree_size = (2 * num_of_leaves) - 1
        server = Server(tree_size)
        client = Client(N, server)
        self.request_queue = queue.Queue()
        self.result_queue = queue.Queue()
        if self.mode == 1:
            print('Running with default client- no Timing Channel suppression', color='blue')
            self.client = DefaultClient(N=N, client=client, server=server, request_queue=self.request_queue,
                                        result_queue=self.result_queue, gui_update_callback=gui_update)
        if self.mode == 2:
            print('Running Ascend client', color='blue')
            rate = input('Enter rate of requests per second (it is recommended to pick 1-2): ')
            if not rate.isnumeric():
                print('Rate must be a positive number. Exiting.', color='red')
                exit(1)
            self.client = AscendClient(N=N, client=client, server=server, request_queue=self.request_queue,
                                       result_queue=self.result_queue, rate=1/int(rate), gui_update_callback=gui_update)
        if self.mode == 3:
            print('Running Learning Ascend client', color='blue')
            mode = input('Enter mode (power/performance): ')
            if mode not in ['power', 'performance']:
                print('Invalid mode. Exiting.', color='red')
                exit(1)
            self.client = LearningAscendClient(N=N, client=client, server=server, request_queue=self.request_queue,
                                               result_queue=self.result_queue, mode=mode, gui_update_callback=gui_update)
        # Create a button to stop the client
        stop_button = tk.Button(self.root, text="Stop Client", command=self.stop_client)
        stop_button.pack()

        # Start the `run()` function in a new thread to avoid blocking the GUI
        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.start()

        # Run the Tkinter main loop in the main thread
        self.root.mainloop()

    def run(self):
        while True:
            request = input('\nChoose operation number: (1)store | (2)retrieve | (3)delete | (0)exit\n')
            if request == STORE:
                self.handle_store()
            elif request == RETRIEVE:
                self.handle_retrieve()
            elif request == DELETE:
                self.handle_delete()
            elif request == EXIT:
                print('\nExiting')
                self.client.stop()
                break
            else:
                print('Invalid option. Please choose from: 1/2/3/0', color='red')

    def stop_client(self):
        """Stop the client and close the Tkinter window."""
        if self.client:
            self.client.stop()  # Stop the client if it's running
        self.root.quit()  # Close the Tkinter window
        exit(0)  # Exit the program

    def handle_store(self):
        print('\n--- STORE ---', color='blue')
        data_id = self.get_data_id_from_user()
        data = input('Insert data (string of 4 characters): ')
        if len(data) != 4:
            print('Data must be a string of 4 characters. Please try again.', color='red')
            return
        self.request_queue.put(('store', data_id, data))
        print('Store operation completed.', color='green')

    def handle_retrieve(self):
        print('\n--- RETRIEVE ---', color='blue')
        data_id = self.get_data_id_from_user()
        self.request_queue.put(('retrieve', data_id, None))
        data = self.result_queue.get()
        print(f'Data retrieved: {data}', color='green')

    def handle_delete(self):
        print('\n--- DELETE ---', color='blue')
        data_id = self.get_data_id_from_user()
        self.request_queue.put(('delete', data_id, None))
        print('Delete operation completed.', color='green')

    def get_data_id_from_user(self) -> int:
        data_id = input('Insert data id (must be integer): ')
        while not data_id.isdigit():
            data_id = input('data id must be integer. choose again: ')
        return int(data_id)
