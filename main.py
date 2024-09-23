import sys
from demo import *

if __name__ == '__main__':
    option = sys.argv[1]
    mode = sys.argv[2]
    if mode == 'default':
        mode = 1
    elif mode == 'ascend':
        mode = 2

    if option == 'demo':
        demo1()
    elif option == 'test':
        demo2(mode)
    else:
        print("Enter valid arg.")
