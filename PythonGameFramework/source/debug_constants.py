### PARAMETERS ###
INT = 0
STRING = 1
FLOAT = 2

FALSE = 0
TRUE = 1

DEBUG_MENU =\
'''
Select a Debug Option (or -99 to exit debugger):
0) Quit
1) Change Character Speed
2) Edit Scenery
3) Edit Tilemap
>>>'''
QUIT = 0
EXIT_DEBUGGER = -99
EXIT_DEBUGGER_STR = '-99'
CHAR_SPEED = 1
SCENERY = 2
TILEMAP = 3

MOVESPEED_MENU=\
'''
Enter an integer value for character Move Speed, or -99 to exit debugger.
(0 is no movement, 10 is average, 30 is insane)
>>>'''
MIN_MOVE_SPEED = -10000
MAX_MOVE_SPEED = 10000

SCENERY_MENU=\
'''
Choose Scenery Type (or -99 to exit debugger)
0) Quit
1) Background
2) Foreground 
>>>'''
BACKGROUND = 1
FOREGROUND = 2

PANORAMA_PROMPT='''or 0 to Cancel, or -99 to exit debugger
>>>'''

TILEMAP_MENU=\
'''
Choose Tilemap Type (or -99 to exit debugger)
0) Quit
1) Lower
2) Upper
3) Barrier
>>>'''
LOWER = 1
UPPER = 2
BARRIER = 3

SCENERY_EDIT_MENU =\
'''
What will you change? (or -99 to exit debugger)
0) Quit
1) filePath (load new image)
2) visible sections
3) scrolling
4) alpha (True or False)
5) layer
6) motion X (True or False)
7) motion Y (True or False)
8) motion_x_pxs
9) motion_y_pxs
10) animated (True or False_
11) animated frames per second
>>>
'''
FILEPATH = 1
VISIBILE_SECTIONS = 2
SCROLLING = 3
ALPHA = 4
LAYER = 5
MOTIONX = 6
MOTIONY = 7
MOTION_X_PXS = 8
MOTION_Y_PXS= 9
ANIMATED = 10
ANIMATED_FPS = 11

GET_FILEPATH='''Enter a filepath to a panorama image:
>>>'''

ALLOWED_IMAGETYPES = ('.jpg', '.png', '.gif', '.bmp', '.pcx', '.tga', '.tif', '.lbm', '.pbm', '.pgm', '.ppm', '.xpm',
                     '.JPG', '.PNG', '.GIF', '.BMP', '.PCX', '.TGA', '.TIF', '.LBM', '.PBM', '.PGM', '.PPM', '.XPM')

VISIBILE_MENU=\
'''
Add or Delete a Section? (or -99 to exit Debugger)
0) Quit
1) Delete
2) Add
>>>
'''
DELETE_VISIBILITY = 1
ADD_VISIBILITY = 2

GET_MOTION =\
'''
0) False
1) True
>>>
'''