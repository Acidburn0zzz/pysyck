
import unittest

import _syck, syck


class Test1(unittest.TestCase):

    def testme(self):
        pass

class Test2(unittest.TestCase):

    def testmetoo(self):
        pass

def main(module='__main__'):
    unittest.main(module)

if __name__ == '__main__':
    main()

