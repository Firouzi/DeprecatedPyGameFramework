'''
Created on Mar 1, 2017

@author: Robert
'''

#should create the init function for the game first (since need a sound effect player etc

import unittest
from setup import playerFactory
from actors import SimpleBox
from event import EventSound

class Test(unittest.TestCase):

    def setUp(self):
        actor = SimpleBox()
        self.player = playerFactory(actor)
        
    def test_actionMove(self):
        self.player.actionMove('up')
        self.player.actionMove('down')
        self.player.actionMove('left')
        self.player.actionMove('right')

    def test_actionColorSwap(self):
        self.assertEqual(type(self.player.defaultAction()) is EventSound,True)

    def tearDown(self):
        pass
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()