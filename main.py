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
