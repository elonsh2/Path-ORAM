import sys
from demo import *

if __name__ == '__main__':
    option = sys.argv[1]
    if option == 'demo':
        demo1()
    elif option == 'test':
        demo2()
    else:
        print("Enter valid arg.")


# import tkinter as tk
# from demo import demo1, demo2
#
# def run_demo1():
#     demo1()
#
# def run_demo2():
#     demo2()
#
#
#
# def on_select(option):
#     if option == 'Demo 1':
#         run_demo1()
#     elif option == 'Demo 2':
#         run_demo2()
#
# # Create the main window
# root = tk.Tk()
# root.title("Demo Selector")
#
# # Create buttons
# button1 = tk.Button(root, text="Demo 1", command=lambda: on_select('Demo 1'))
# button1.pack(pady=10)
#
# button2 = tk.Button(root, text="Demo 2", command=lambda: on_select('Demo 2'))
# button2.pack(pady=10)
#
# # Start the GUI event loop
# root.mainloop()