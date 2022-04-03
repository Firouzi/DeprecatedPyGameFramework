import parameters as PRAM
import sys, importlib
from game_level import LevelData, GameMenu, GameCutscene
from event import EventLoadMenu, EventSetInput
from debug import DebugLooper

class Game:
    def __init__(self, player = None, 
                 musicPlayer = None, 
                 soundPlayer = None, 
                 renderer = None,
                 gameCamera = None,
                 eventHandler = None):
        self.player = player
        self.musicPlayer = musicPlayer
        self.soundPlayer = soundPlayer
        self.renderer = renderer
        self.eventHandler = eventHandler
        
        self.gameCamera = gameCamera
        
        #explicitly name Class fields
        self.gameEvents = [] 
        self.keydownEvents = []
        self.gameScene = None
        self.levelData = None
        self.inputHandler = None
        self.runDebug = False


    def gameStartup(self):
        self.addEvent(EventLoadMenu(PRAM.MENU_TEST1))
#         self.addEvent(EventLoadLevel(PRAM.LEV_TEST1))

    def loadLevel(self, eventLoadLevel):
        self.unloadScene()

        self.addEvent(EventSetInput(PRAM.INPTYPE_NORMAL))
        self.levelData = LevelData()
        self.levelData.loadLevel(eventLoadLevel.levelIndex)
        self.levelData.addActor(self.player.actor) #add the player character to the level actors list
        
        self.player.setPosition(eventLoadLevel.startingPosition)
        
        self.gameCamera.maxPosition = [  #TODO - may need to modify this to create a bounding box
            (self.levelData.size[0] - PRAM.DISPLAY_TILE_WIDTH)*PRAM.TILESIZE,
            (self.levelData.size[1] - PRAM.DISPLAY_TILE_HEIGHT)*PRAM.TILESIZE]
        
        self.renderer.loadAssets(self.levelData)
        self.eventHandler.borders = self.levelData.borders
        self.eventHandler.eventTiles = self.levelData.eventTiles

       #TODO - add to the renderMethod lists based on the levelData
        #currently triggered on the tile
#         for event in self.gameScene.levelEvents: #the triggers need to be initialized for level events
#             if type(event) is LevelTriggerTouch:
#                 if event.subject == 'player':
#                     self.player.addListener(PRAM.LISTENER_MOVE, event)
#                     event.subject = self.player

#         self.gameScene.addActor(self.player.actor) #add the player character to the level actors list


    def loadMenu(self, menuFile):
        self.unloadScene()
        sys.path.append(PRAM.MENU_PATH)
        menu = importlib.import_module(menuFile)
        sys.path.pop()

        #TODO this object is basically a deprecated placeholder
        self.gameScene = GameMenu(
            [],#self.loadActors(menu.actors), #returns an actorWrapper object
            [],#self.loadImages(menu.scenery, False), #returns a sceneryWrapper object
            [], #levelEvents
            menu.gameEvents,
            []) #menu.layout)

        for event in self.gameScene.gameEvents:
            self.addEvent(event)

    def loadCutscene(self, cutsceneFile): #TODO - everything about this
        self.unloadScene()
        sys.path.append(PRAM.MENU_PATH)
        cutscene = importlib.import_module(cutsceneFile)
        sys.path.pop()
        self.gameScene = GameCutscene(cutscene) 

    def render(self):
        self.renderer.render()

    # Halt any running events, unload any assets, etc
    def unloadScene(self):
        #TODO - empty game event queue
        self.soundPlayer.stopSound()
        self.musicPlayer.stopSong()

    def addEvent(self,event):
        self.gameEvents.append(event)

    def runDebugLoop(self):
        self.runDebug = False
        debugLooper = DebugLooper(self)
        debugLooper.start()