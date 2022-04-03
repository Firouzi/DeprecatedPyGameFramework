'''
Created on Feb 24, 2017

@author: Robert
'''

import pygame
from parameters import *
from setup import soundPlayerFactory, playerFactory, eventHandlerFactory
from render import Renderer
from game import Game
from input import InputHandler, ButtonMap
from camera import GameCamera

### SETUP ###
pygame.init()
flags = pygame.DOUBLEBUF | pygame.HWSURFACE #| pygame.FULLSCREEN #TODO
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags)
CLOCK = pygame.time.Clock() 
DONE = False

### GAME ENGINE ###
musicPlayer, soundPlayer = soundPlayerFactory()
renderer = Renderer(screen)
gameCamera = GameCamera()
player = playerFactory()
game = Game(player, musicPlayer, soundPlayer, renderer, gameCamera)
inputHandler = InputHandler(game, player, ButtonMap())
eventHandler = eventHandlerFactory(game)
eventHandler.renderer = renderer 
game.inputHandler = inputHandler
game.eventHandler = eventHandler
renderer.camera = gameCamera

game.gameStartup()
while not DONE:
        for event in pygame.event.get():         
            if event.type == pygame.QUIT:
                DONE = True #TODO make this an input that creates a quit event?
            if event.type == pygame.KEYDOWN:
                game.keydownEvents.append(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.keydownEvents.append(event)
            #TODO can tell pygame to only check for specific events
        game.keysPressed = pygame.key.get_pressed()
        
        inputHandler.handleInputs() #iterates through the keydown and keypressed events
        eventHandler.handleEvents()
        
        game.render()
        
        #debug helper, draw the tile gridlines
        # for i in range(35):
        #     pygame.draw.line(screen, PRAM.COLOR_BLACK,(0, 48*i), (1600, 48*i))
        #     pygame.draw.line(screen, PRAM.COLOR_BLACK,(48*i, 0), (48*i, 900))

        if game.runDebug:
            game.runDebugLoop() #if debug is activated ented debug mode

        pygame.display.update() #TODO if passing updated recs, this is more efficient
        CLOCK.tick(GAME_FPS) #60 FPS

#this will only run if the module is run as the main module, not if imported.
if __name__ == '__main__':
    pass #nop

