#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    if sys.version_info[:2] < (3, 4):
        sys.exit('Python version must be at least 3.4')

    from builder import Builder

    root_path = os.path.dirname(os.path.abspath(__file__))
    Builder(root_path).main()
