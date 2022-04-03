'''
Created on Mar 4, 2017

@author: Robert
'''

import unittest
import parameters as PRAM
from actors import SimpleBox

class Test(unittest.TestCase):

    def setUp(self):
        self.simpleBox=SimpleBox(PRAM.COLOR_ORANGE)

### SolidBackground() ###
    def test_colorSwap(self):
        self.assertEqual(self.simpleBox.color, PRAM.COLOR_ORANGE)
        self.simpleBox.colorSwap()
        self.assertEqual(self.simpleBox.color, PRAM.COLOR_BLUE)
        self.simpleBox.colorSwap()
        self.assertEqual(self.simpleBox.color, PRAM.COLOR_ORANGE)

    def tearDown(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()