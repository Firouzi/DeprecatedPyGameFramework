'''
Created on Mar 4, 2017

@author: Robert
'''
import unittest
import pygame
import parameters as PRAM
from render import Renderer
from actors import SimpleBox
from input import ButtonMap, InputHandler
from event import EventHandler
from setup import playerFactory, soundPlayerFactory
from game import Game
from event import EventLoadLevel
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
        
    def test_renderScenery(self):
        self.game.gameStartup()
        self.eventHandler.handleEvents()
        self.renderer.renderScenery(self.game.gameScene.sceneryWrapper)
        pygame.display.flip()
        
    def test_renderActors(self):
        self.game.gameStartup()
        self.game.addEvent(EventLoadLevel(PRAM.LEV_TEST1))
        self.eventHandler.handleEvents()
        self.renderer.renderActors(self.game.gameScene.actorsWrapper)
        pygame.display.flip()
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()