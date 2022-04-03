'''
Created on Feb 24, 2017

@author: Robert
'''
import os

### PATHS ###
REAL_PATH =  os.path.realpath('')
MUSIC_PATH = REAL_PATH+'\\dir_sound\\dir_music\\'
AMBIANCE_PATH = REAL_PATH+'\\dir_sound\\dir_ambiance\\'
SOUND_PATH = REAL_PATH+'\\dir_sound\\dir_soundeffects\\'
IMAGE_PATH = REAL_PATH+'\\dir_image\\'
LEVEL_PATH = REAL_PATH+'\\dir_levels\\'
MENU_PATH = REAL_PATH+'\\dir_menu\\'
CUTSCENE_PATH = REAL_PATH+'\\dir_cutscene\\'
TILE_PATH = IMAGE_PATH +'dir_tilesets\\'

'''
a 1600x896 screen gives about 50x32 tiles of size 32
33x19 of size 48 tiles
This makes a ~100x100 tile map reasonable, and provides a good 5 screens 
of scrolling

'''

### SCREEN ###
DISPLAY_WIDTH = 1600 #TODO -lowering these greatly boosts performance
DISPLAY_HEIGHT = 900
TILESIZE = 48
TILEMAP_MAX_WIDTH = 8 #tiles
TILEMAP_MAX_HEIGHT = 20 # tiles 8*20 = 160 lower tiles and 160 upper tiles per map
DISPLAY_TILE_WIDTH = DISPLAY_WIDTH // TILESIZE + 2 #make sure to render tiles on the edge
DISPLAY_TILE_HEIGHT = DISPLAY_HEIGHT // TILESIZE + 2
#determine when to pan the camera with the char
CAMERA_WIDTH = DISPLAY_WIDTH // 5 #the min number of pixels from char to edge of screen
CAMERA_HEIGHT = DISPLAY_HEIGHT // 4
GAME_FPS = 60

### INPUT TYPES###
INPTYPE_OBSERVER = 'observe'
INPTYPE_MENU = 'menu'
INPTYPE_NORMAL = 'normal'

### TRIGGER TYPES ###
TRIG_TOUCH = 'touch'
TRIG_ACTION = 'action'

UP = 3
DOWN = 2
LEFT = 0
RIGHT = 1

### EVENT TYPES ###
KEYDOWN = 2
CLICKDOWN = 5

### KEYS ### - pygame.<keyname>
INPUT_ACTION = 32 #pygame space bar
INPUT_STATUS = 13 #pygame enter key
INPUT_DEBUG = 305 #pygame KMOD_RCTRL key
INPUT_UP = 273
INPUT_DOWN = 274
INPUT_LEFT = 276
INPUT_RIGHT = 275
INPUT_LEFTCLICK = 1
INPUT_WHEELCLICK = 2
INPUT_RIGHTCLICK = 3
INPUT_WHEELUP = 4
INPUT_WHEELDOWN = 5


### ACTORS ###
SIMPLE_BOX_WIDTH = 48
SIMPLE_BOX_HEIGHT = 96
BOX_FUDGE = 3 #Debug param to aproximate character sprite

### LISTENER TYPES ###
LISTENER_MOVE = 'move'

### COLORS ###
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 128, 255)
COLOR_ORANGE = (255, 100, 0)
COLOR_GREEN = (100, 255, 0)



### IMAGES ###
IMAGE_LIBRARY = ['ball.png'] #may not be needed

### IMAGE MAP ###
IMG_BALL = 'ball.png'
IMG_TEST = 'testsprite.png'
BACKGROUND_TEST = 'background.jpg' 

### SOUNDTRACK ###
MUSIC_PLAYLIST = [
    'ERROR',
    'saga7-Wind',
    'saga7-Water']

AMBIANCE = ['city']

SOUNDEFFECTS = [
    'ERROR',
    'click']

### SONGMAP ###
SONG_SAGAWATER = 'saga7-Water'
SONG_SAGAWIND = 'saga7-Wind'
SONG_TEST = 'testsong'
SONG_ERROR = 'ERROR'

### AMBIANTMAP ###
AMB_CITY = 'city'

### SOUNDMAP ###
SOUND_COLORSWAP = 'click'
SOUND_ERROR = 'ERROR'
SOUND_TEST = 'testeffect'

### GAME LEVELS ###
LEVEL_LIBRARY = ['level_test01'] #may not be needed

### LEVEL MAP ###
LEV_TEST1 = 'level_test01'
LEV_TEST2 = 'level_test02'
LEV_INDEX1 = 1

### GAME MENUS ###
MENU_LIBRARY = ['menu_test01']

### MENU MAP ###
MENU_TEST1 = 'menu_test01'




