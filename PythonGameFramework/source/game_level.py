import parameters as PRAM
import database
import json #to parse the lists in the DB
from scenery import PanoramicImage, Tilemap

class LevelData:
    def __init__(self,
                 name = '',
                 size = (10,10),
                 lowerTileMap = None, #Tilemap oject
                 upperTileMap = None,
                 lowerTiles = (), #displayed below all actors
                 upperTiles = (), #displayed above all actors
                 borders = (), #4 bits, one to represent each direction
                 eventTiles = (), #Events are indexed based on coordiante pairs
                 actors = (), #static or dynamic, displayed in order of Y coords
                 backgrounds = (), #list of background objects
                 foregrounds = (), #list of foreground objects
                 gameEvents = () #added to event queue on level load
                 ):
        self.name = name
        self.size = size
        self.lowerTileMap = lowerTileMap
        self.upperTileMap = upperTileMap
        self.borders = borders
        self.eventTiles = eventTiles
        self.actors = actors 
        self.backgrounds = backgrounds #list of background objects
        self.foregrounds = foregrounds
        self.gameEvents = gameEvents
    
    
    def loadLevel(self, index):
        self.loadLevelData(index)
        self.loadLevelEvents(index)
        self.loadGameEvents(index)
        self.loadActors(index)
        self.loadBackgrounds(index)
        self.loadForegrounds(index)

    #Loads the level name, size, tile maps and border map
    def loadLevelData(self, index):
        row = database.getLevelData(index)
        if row is None:
            return False

        self.name = row[1]
        self.size = (row[2],row[3])

        lowerTiles = json.loads(row[4]) #unpack the strings into 2d lists
        upperTiles = json.loads(row[5])
        borders = json.loads(row[6])
        
        for i in range(len(borders)):
            borders[i] = tuple(borders[i])  
        borders = tuple(borders)

        self.borders = borders

        #load tilemap data from the DB
        tileMaps = database.getTileMaps(index)  # expect lower, and upper as list
        if tileMaps is None or len(tileMaps) != 2:
            return False

        if tileMaps[0][6] == 'lower':
            lower = 0
            upper = 1
        else:
            lower = 1
            upper = 0

        self.lowerTileMap = Tilemap(tileMaps[lower][2],  # filepath
                               tileMaps[lower][3],  # tilesize_px
                               tileMaps[lower][4],  # height_tiles
                               tileMaps[0][5],  # width_tiles
                               lowerTiles,  # The mapping of each tile on the level to the iomage
                               tileMaps[lower][6], # type
                               tileMaps[lower][7], # alpha
                               tileMaps[lower][8], # isAnimated
                               tileMaps[lower][9], # animatedIndex
                               tileMaps[lower][10], # Frames
                               tileMaps[lower][11]) # fps

        self.upperTileMap = Tilemap(tileMaps[upper][2], # Filepath
                               tileMaps[upper][3], # tilesize_px
                               tileMaps[upper][4], # height_tiles
                               tileMaps[0][5], # width_tiles
                               upperTiles, # The mapping of each tile on the level to the iomage
                               tileMaps[upper][6], # type
                               tileMaps[upper][7], # alpha
                               tileMaps[upper][8], # isAnimated
                               tileMaps[upper][9], # animatedIndex
                               tileMaps[upper][10], # Frames
                               tileMaps[upper][11]) # fps


    def addActor(self, actor):
        self.actors = list(self.actors)
        self.actors.append(actor)
        self.actors = tuple(self.actors)

    def loadLevelEvents(self, index):
        self.eventTiles = {}
        print(index) #temp code to remove warning from pycharm, remove once method is implemented
        pass

    def loadGameEvents(self, index):
        pass

    def loadActors(self, index):
        pass

    def loadBackgrounds(self, index):
        self.backgrounds = list()
        backgrounds = database.getBackgrounds(index)

        for background in backgrounds:
            visibleSections = json.loads(background[5]) #unpack the strings into 2d lists
            for i in range(len(visibleSections)): #change to tuple for speed
                visibleSections[i] = tuple(visibleSections[i])
            visibleSections = tuple(visibleSections)
            
            scrolling = json.loads(background[6])
            for i in range(len(scrolling)): #change to tuple for speed
                scrolling[i] = tuple(scrolling[i])
            scrolling = tuple(scrolling)
                        
            panoramicImage = PanoramicImage(background[2], #filepath
                                            (background[3], background[4]), #size
                                             visibleSections,
                                             scrolling,
                                             background[7], #alpha
                                             background[8], #layer
                                             background[9], #isMotion_X TODO need to pull from DB
                                             background[10], #isMotion_Y
                                             background[11], #motionX_pxs
                                             background[12], #motionY_pxs
                                             background[13], #isAnimated
                                             background[14], #fps
                                             background[15], #numbImages
                                             background[16])  #imageType

            self.backgrounds.append(panoramicImage)
        self.backgrounds = tuple(self.backgrounds)
    
    def loadForegrounds(self, index):
        self.foregrounds = list()
        foregrounds = database.getForegrounds(index)
        
        for foreground in foregrounds:
            visibleSections = json.loads(foreground[5]) #unpack the strings into 2d lists
            for i in range(len(visibleSections)): #change to tuple for speed
                visibleSections[i] = tuple(visibleSections[i])
            visibleSections = tuple(visibleSections)
            
            scrolling = json.loads(foreground[6])
            for i in range(len(scrolling)): #change to tuple for speed
                scrolling[i] = tuple(scrolling[i])
            scrolling = tuple(scrolling)
                        
            panoramicImage = PanoramicImage(foreground[2],  #filepath
                                            (foreground[3], foreground[4]),  #size
                                             visibleSections,
                                             scrolling,
                                             foreground[7],  #alpha
                                             foreground[8],  #layer
                                             foreground[9],  # Motion_X
                                             foreground[10], # Motion_Y
                                             foreground[11],  # motionX_pxs
                                             foreground[12],  # motionY_pxs
                                             foreground[13], #isAnimated
                                             foreground[14]) #fps
            
            self.foregrounds.append(panoramicImage)

        self.foregrounds = tuple(self.foregrounds)

# Data container for a game menu, which can be loaded as an event (akin to loading a level).
#     EG load the title screen, or options, save/load etc...
class GameMenu:
    def __init__(self,
                 actorsWrapper = None,
                 sceneryWrapper = None,
                 levelEvents = (),
                 gameEvents = (),
                 layoutWrapper = ()):
        self.actorsWrapper = actorsWrapper
        self.sceneryWrapper = sceneryWrapper
        self.levelEvents = levelEvents
        self.gameEvents = gameEvents
        self.layoutWrapper = layoutWrapper


# Loads a cutscene
class GameCutscene: #TODO
    def __init__(self, cutscene = ()):
        self.cutscene = cutscene


# Defines the event that is triggered on a level tile, and how it is triggered
#     Defines number of times that event can be triggered (or -1 for infinite)
class LevelEvent:
    def __init__(self, trigger, gameEvent, triggers = -1):
        self.trigger = trigger
        self.gameEvent = gameEvent
        self.triggers = triggers

# Level events require a trigger event (whereas gameEvents run immediately)
#     This event triggers if it is touched. Default subject is player.
#     size and position can be hardcoded, or set as the size and position of
#     another actor (if the event should move with an actor)
#     level tiles can also trigger an event if touched
class LevelTriggerTouch:
    def __init__(self, gameEvent, size = (0,0) , position = (0,0), subject = 'player', actor = None):
        self.gameEvent = gameEvent
        self.size = size
        self.position = position
        self.subject = subject
        self.actor = actor

#TODO this method requires too much knowledge of other classes it appears
    # def notify(self):
    #     if self.subject.position[0] >= self.position[0] and self.subject.position[0] <= self.position[0] + self.size[0]:
    #         if self.subject.position[1] >= self.position[1] and self.subject.position[1] <= self.position[1] + self.size[1]:
    #             return self.gameEvent
    #     return None


    
    