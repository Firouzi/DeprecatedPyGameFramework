'''
Created on Feb 27, 2017

This module is not yet robust, but creating a unit test mainly to test
the framework

@author: Robert
'''
import unittest
import parameters as PRAM
from scenery import SolidBackground, StaticSprite

class Test(unittest.TestCase):

    def setUp(self):
        self.solidBackground=SolidBackground(PRAM.COLOR_BLACK)
        self.staticSprite=StaticSprite(PRAM.IMAGE_PATH+PRAM.IMG_TEST, (20,20))

### SolidBackground() ###
    def test_colorChange(self):
        self.assertEqual(self.solidBackground.color, PRAM.COLOR_BLACK)
        self.assertEqual(self.solidBackground.colorChange(PRAM.COLOR_ORANGE), True)
        self.assertEqual(self.solidBackground.color, PRAM.COLOR_ORANGE)

    def tearDown(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()