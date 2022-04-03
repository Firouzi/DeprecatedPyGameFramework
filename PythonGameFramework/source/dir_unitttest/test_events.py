'''
Created on Mar 4, 2017

@author: Robert
'''
import unittest, pygame
import parameters as PRAM
from setup import soundPlayerFactory, playerFactory
from actors import SimpleBox
from render import Renderer
from game import Game
from event import EventHandler, EventLoadMenu, EventLoadLevel
from input import InputHandler, ButtonMap

class SudoKeyEvent():
    def __init__(self, key):
        self.key = key

class Test(unittest.TestCase):
    def setUp(self):
        pygame.init()  # @UndefinedVariable
        screen = pygame.display.set_mode((PRAM.DISPLAY_WIDTH, PRAM.DISPLAY_HEIGHT))
        buttonMap = ButtonMap()
        actor = SimpleBox()
        musicPlayer, soundPlayer = soundPlayerFactory()
        self.renderer = Renderer(screen)
        player = playerFactory(actor)
        
        self.game = Game(player, musicPlayer, soundPlayer, self.renderer)
        self.inputHandler = InputHandler(self.game, player, buttonMap)
        self.eventHandler = EventHandler(self.game)
        self.game.eventHandler = self.eventHandler
        self.game.inputHandler = self.inputHandler
        
    def test_eventHandler(self):
        self.game.addEvent(EventLoadMenu(PRAM.MENU_TEST1))
        self.game.addEvent(EventLoadLevel(PRAM.LEV_TEST1))
        self.eventHandler.handleEvents()

    def test_inputHandler(self):                
        ### sudo create key events ###
        keyPressDefault = SudoKeyEvent(PRAM.INPUT_ACTION)
        self.game.keydownEvents=[]        
        self.game.keydownEvents.append(keyPressDefault)
        self.game.keysPressed = list(pygame.key.get_pressed())
        self.game.keysPressed[PRAM.INPUT_UP] = 1
        self.game.keysPressed[PRAM.INPUT_DOWN] = 1
        self.game.keysPressed[PRAM.INPUT_LEFT] = 1
        self.game.keysPressed[PRAM.INPUT_RIGHT] = 1
        
        ### test input for level mode ###  
        self.inputHandler.handleInputs()
        
        ### test input events for menu mode ###
        self.game.keydownEvents.append(keyPressDefault)
        self.game.addEvent(EventLoadMenu(PRAM.MENU_TEST1))
        self.eventHandler.handleEvents()
        self.inputHandler.handleInputs()        
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()