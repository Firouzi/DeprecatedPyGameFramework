'''
Created on Mar 11, 2017

temporary script to generate a level file

@author: Robert
'''

import os

topTile = "LevelTile('grass','','',0b0001,None)"
tileXleft = "LevelTile('grass','','',0b0010,None)"
tileXright = "LevelTile('grass','','',0b0100,None)"
bottomTile = "LevelTile('grass','','',0b1000,None)"
midTile = "LevelTile('grass','','',0b0000,None)"
trunkTile = "LevelTile('grass','trunk','',0b1111,None)"
treeTile = "LevelTile('grass','','tree',0b0000,None)"

def writeRow(file, tile, count, tree = False, trunk = False):
    file.write('     (')
    file.write(tileXleft)
    file.write(', ')
    for i in range(count-2):
        if i%8==0:
            if tree:
                file.write(treeTile)
            elif trunk:
                file.write(trunkTile)
            else:
                file.write(tile)
        else:    
            file.write(tile)
        file.write(', ')
    file.write(tileXright)
    file.write('),\n')

print('level generator start')

levelName = 'level_test_lg.py'
levelSize = (150,150)



folder = 'dir_levels_generated'
directory =  os.path.realpath('')+'\\'+folder+'\\'
if os.path.isdir(directory) == False:
    os.makedirs(directory)
levelFile = open(directory+levelName, 'w')

levelFile.write('size = (' + str(levelSize[0])+','+str(levelSize[1])+')\n\n')
levelFile.write('layout = (\n')
writeRow(levelFile,topTile,levelSize[0])

i =1
while i<levelSize[0]:
    if i%8==7 or i%8==6:
        writeRow(levelFile,midTile,levelSize[0], True)
    elif i%8==0 or i%8==1:
        writeRow(levelFile,midTile,levelSize[0], False, True)
    else:
        writeRow(levelFile,midTile,levelSize[0])
    i+=1

writeRow(levelFile,bottomTile,levelSize[0])

levelFile.write('     )\n')
levelFile.close()



print('level generator end')
