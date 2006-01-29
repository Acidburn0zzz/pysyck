
import unittest

from test_node import *
from test_parser import *
from test_loader import *
from test_emitter import *
from test_dumper import *
from test_pickle import *
from test_threads import *
from test_unicode import *

def main(module='__main__'):
    unittest.main(module)

if __name__ == '__main__':
    main()

