from game_level import LevelData #@UndefinedVariable
import sys
sys.path.append("C:\\Users\\Robert\\repositories\\gameDev\\swordFightProto\\dir_database\\")
import createDatabase as DB # @UndefinedVariable
import pickle
import random

# This will create a simple practice level
# blank border, with trees intersperced
FILENAME = 'Level_test_6'
WIDTH = 150
HEIGHT = 150
BORDER = 15
TREESPACING = 9
LOWER_TILEMAP = 'lower.bmp'
UPPER_TILEMAP = 'upper.bmp'

TILE_VARIANCE = 50 #out of how many tiles do we have different than the normal
MAX_TILE_INDEX = 8*20

BLANK_TILE = 0
GROUND_TILE = 1
BARRIER_TILE = 2
OVERHEAD_TILE = 1

'''
Barriers
  0
1   2
  3
represents bit position in 4 bit string
1 for barrier in that direction
EG
if a tile cannot be entered from the left =0b0010
if i tile cannot be entered from left or bottom = 0b1010  
'''
CLEAR =  0b0000 #0
TOP =    0b0001 #1
LEFT =   0b0010 #2
RIGHT =  0b0100 #4
BOTTOM = 0b1000 #8

backgrounds = []
foregrounds = []
gameEvents = []
actors = []

#Lower tiles are an array of ints, the ints are a key to the correct tile in the tilemap
def createLower():
    matrix = [ [GROUND_TILE] * WIDTH for _ in range(HEIGHT)]
        
    for i in range(HEIGHT): #create blank borders and some variety in the ground tiles 
        for j in range(WIDTH):
            if i < BORDER or i >= HEIGHT - BORDER or j < BORDER or j >= WIDTH-BORDER:
                matrix[i][j] = BLANK_TILE
            elif random.randint(0,TILE_VARIANCE) == TILE_VARIANCE//2: #add some randomness to the tiles
                matrix[i][j] = (random.randint(1,MAX_TILE_INDEX)//2)*2 + 1 #odd numbers are ground tiles
                if matrix[i][j] > MAX_TILE_INDEX:
                    matrix[i][j] = MAX_TILE_INDEX - 1
                    
                
    
    #add trees
    for i in range(HEIGHT):
        if i % TREESPACING == 0 and i > BORDER and i < HEIGHT - BORDER:
            for j in range(WIDTH):
                if j % TREESPACING == 0 and j > BORDER and j < WIDTH - BORDER:
                    if i < HEIGHT - 4:
                        matrix[i+2][j] = (random.randint(2,MAX_TILE_INDEX)//2) * 2 #even numbers are barriers
                        matrix[i+3][j] = (random.randint(2,MAX_TILE_INDEX)//2) * 2 #adding some variance to tiles
                               
    return matrix

#Upper tiles are an array of ints, the ints are a key to the correct tile in the tilemap    
def createUpper():
    matrix = [ [BLANK_TILE] * WIDTH for _ in range(HEIGHT)]
            
    #add trees
    for i in range(HEIGHT):
        if i % TREESPACING == 0 and i > BORDER and i < HEIGHT - BORDER:
            for j in range(WIDTH):
                if j % TREESPACING == 0 and j > BORDER and j < WIDTH - BORDER:
                    if i < HEIGHT - 4:
                        matrix[i][j] = random.randint(1,MAX_TILE_INDEX) #adding some variance to treetops
                        matrix[i+1][j] = random.randint(1,MAX_TILE_INDEX)
                               
    return matrix

#border tiles are an array of 4bit sequences, if the bit is 1, that direction is not traversable on this tile
def createBorders(lowerTiles):
    matrix = [ [CLEAR] * WIDTH for _ in range(HEIGHT)]
        
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if i == 0:
                matrix[i][j] |= TOP
            if i == HEIGHT-1:
                matrix[i][j] |= BOTTOM
            if j == 0:
                matrix[i][j] |= LEFT
            if j == WIDTH - 1:
                matrix[i][j] |= RIGHT
            if lowerTiles[i][j] != 0 and lowerTiles[i][j]%2 == 0: #even numbers are barriers
                matrix[i][j] |= LEFT | RIGHT | TOP | BOTTOM   
                       
    return matrix

def saveLevelData(levelData): #TODO update this to match the Class
    DB.addLevelDataRow(FILENAME, levelData.size[0], levelData.size[1], levelData.lowerTiles, levelData.upperTiles,levelData.borders)


#this will only run if the module is run as the main module, not if imported.
if __name__ == '__main__':
    levelData = LevelData(FILENAME, (WIDTH,HEIGHT))
    levelData.lowerTiles = createLower()
    levelData.upperTiles = createUpper()
    levelData.borders = createBorders(levelData.lowerTiles)
#     levelData.backgrounds = backgrounds
#     levelData.foregrounds = foregrounds
#     levelData.gameEvents = gameEvents

#     for i in range(0,30):
#         print(levelData.lowerTiles[i])
#     print('')
#     for i in range(len(levelData.lowerTiles)):
#         print(levelData.upperTiles[i])    
#     print('')
#     for i in range(0,30):
#         print(levelData.borders[i])   
    saveLevelData(levelData)
    print('complete')
    
    
    
    
    
    
    
    
    
    
    