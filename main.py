import sys
from Demo import *

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: main.py <mode>")
        sys.exit(1)
    mode = sys.argv[1]
    if mode not in ['1', '2', '3']:
        print('Invalid mode')
        sys.exit(1)
    demo = Demo(int(mode))
    demo.run()
