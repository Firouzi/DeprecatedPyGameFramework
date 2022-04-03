'''
Created on Mar 9, 2017

@author: Robert
'''

import parameters as PRAM

#Return the tile that a pixel position resides in
def calcTileFromPix(pixelPos):
    return (pixelPos[0]//PRAM.TILESIZE,pixelPos[1]//PRAM.TILESIZE)

#The mid point of the character width and lower third of height
def calcCharPix(actorPosition, actorSize):
    return [actorPosition[0] + actorSize[0]//2, actorPosition[1] + actorSize[1]*2//3]

#return the pixel from the tile position + offsets 
def calcPixFromTile(tilePos, xOffset = 0, yOffset = 0):
    return (tilePos[0]*PRAM.TILESIZE + xOffset,tilePos[1]*PRAM.TILESIZE + yOffset)

'''
Note this errors on the side of large (1 pixel into a tile = 1 tile)
Return the ~# of tiles a character takes up
'''
def calcTileSizeFromPix(actorSize):
    if actorSize[0]%PRAM.TILESIZE != 0:
        xMod=1
    else:
        xMod=0
    
    if actorSize[1]%PRAM.TILESIZE != 0:
        yMod=1
    else:
        yMod=0
     
    return [actorSize[0]//PRAM.TILESIZE + xMod, actorSize[1]//PRAM.TILESIZE + yMod]