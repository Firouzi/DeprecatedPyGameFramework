'''
Created on Mar 7, 2017

@author: Robert
'''


import pygame, os

pygame.init()  # @UndefinedVariable
screen = pygame.display.set_mode((500,500))
CLOCK = pygame.time.Clock() 
DONE = False


imageDict = {
    'image1': pygame.image.load(os.path.realpath('')+'\\dir_image\\ball.png').convert(),
    'image2': pygame.image.load(os.path.realpath('')+'\\dir_image\\testsprite.png').convert()}

image = pygame.image.load(os.path.realpath('')+'\\dir_image\\ball.png').convert()

while not DONE:
        for event in pygame.event.get():         
            if event.type == pygame.QUIT:  # @UndefinedVariable
                DONE = True
                
        screen.fill((0,0,0))
        screen.blit(imageDict['image1'], (20,20))
        screen.blit(imageDict['image1'], (80,20))
        screen.blit(imageDict['image2'], (20,80))
        screen.blit(image, (80,80))
        pygame.display.flip()
        CLOCK.tick(60) #60 FPS

print(imageDict['image1'])