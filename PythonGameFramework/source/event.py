import parameters as PRAM
import utility as UTIL

class EventGeneratedBase:
    def __init__(self, eventType = '', params=()):
        self.eventType = eventType
        self.params=params

class EventMove(EventGeneratedBase):
    def __init__(self, character, direction, eventType = 'MOVE', params = ()):
        super(EventMove, self).__init__(eventType, params)
        self.character = character
        self.direction = direction

class EventDefaultAction(EventGeneratedBase):
    def __init__(self, character, eventType = 'DEFAULTACTION', params = ()):
        super(EventDefaultAction, self).__init__(eventType, params)
        self.character = character

# If a character moves, notify any listeners, passing in the character and the
#     listener list
class EventNotifyMove(EventGeneratedBase):
    def __init__(self, character, eventType = 'NOTIFYMOVE', params = ()):
        super(EventNotifyMove, self).__init__(eventType, params)
        self.character = character

class EventSound(EventGeneratedBase):
    def __init__(self, sound, eventType = 'SOUND', params = ()):
        super(EventSound, self).__init__(eventType, params)
        self.sound = sound

class EventSong(EventGeneratedBase):
    def __init__(self, song, eventType = 'SONG', params = ()):
        super(EventSong, self).__init__(eventType, params)
        self.song=song

class EventSetInput(EventGeneratedBase):
    def __init__(self, inputType, eventType = 'SETINPUT', params = ()):
        super(EventSetInput, self).__init__(eventType, params)
        self.inputType = inputType


class EventLoadLevel(EventGeneratedBase):
    def __init__(self, levelIndex, startingPosition = (0,0), eventType = 'LOADLEVEL', params = ()):
        super(EventLoadLevel, self).__init__(eventType, params)
        self.levelIndex = levelIndex
        self.startingPosition = startingPosition

class EventLoadMenu(EventGeneratedBase):
    def __init__(self, menuFile, eventType = 'LOADMENU', params = ()):
        super(EventLoadMenu, self).__init__(eventType, params)
        self.menuFile = menuFile

class EventLoadCutscene(EventGeneratedBase):
    def __init__(self, cutsceneFile, eventType = 'LOADCUTSCENE', params = ()):
        super(EventLoadCutscene, self).__init__(eventType, params)
        self.cutsceneFile = cutsceneFile

class EventHandler:
    def __init__(self, game, eventDict):
        self.game = game
        self.eventDict = eventDict
        
        #explicit declaration of class fields
        self.renderer = None
        self.borders = [] 
        self.eventTiles = {}

    # Runs all the events in the game event queue.  Events can return new events
    #     which are pushed on to the stack and immediately run (be careful of infinite loops!)
    def handleEvents(self):
        while len(self.game.gameEvents) > 0:
            event = self.game.gameEvents.pop()
            if event != '':
                self.eventDict[event.eventType](event)
        return
    
    def runMove(self, event):
        char = event.character
        origin = char.getPosition()
        charPixRelative = UTIL.calcCharPix(char.getPosition(), char.getSize())
        charTileRelative = UTIL.calcTileFromPix(charPixRelative) #relative tile that char appears to stand on
#         layout = self.game.gameScene.layoutWrapper.layout
        
                      
        if event.direction == PRAM.UP:
            char.setDirection(PRAM.UP)
            targetTile = UTIL.calcTileFromPix([charPixRelative[0],charPixRelative[1]-char.moveSpeed])
            if targetTile == charTileRelative:
                char.adjustPosition(0,-char.moveSpeed)
            else:
                if self.borders[targetTile[1]][targetTile[0]] & 0b0001: #barrier in the way
                    char.adjustPosition(0, (targetTile[1]+1) * PRAM.TILESIZE - charPixRelative[1]) #move next to barrier
                else:
                    char.adjustPosition(0,-char.moveSpeed)            
            
        elif event.direction ==PRAM.DOWN:
            char.setDirection(PRAM.DOWN)
            targetTile = UTIL.calcTileFromPix([charPixRelative[0], charPixRelative[1] + char.moveSpeed])
            if targetTile == charTileRelative:
                char.adjustPosition(0, char.moveSpeed)
            else:
                if self.borders[targetTile[1]][targetTile[0]] & 0b1000: #barrier in the way
                    char.adjustPosition(0, targetTile[1] * PRAM.TILESIZE - charPixRelative[1]-1) #move next to barrier
                else:
                    char.adjustPosition(0, char.moveSpeed)
                
        elif event.direction ==PRAM.LEFT:
            char.setDirection(PRAM.LEFT)
            targetTile = UTIL.calcTileFromPix([charPixRelative[0] - char.moveSpeed, charPixRelative[1]])
            if targetTile == charTileRelative:
                char.adjustPosition(-char.moveSpeed, 0) 
            else:
                if self.borders[targetTile[1]][targetTile[0]] & 0b0010: #barrier in the way
                    char.adjustPosition((targetTile[0]+1) * PRAM.TILESIZE - charPixRelative[0], 0) #move next to barrier
                else:
                    char.adjustPosition(-char.moveSpeed, 0)
                                                                          
        else: # 'right'
            char.setDirection(PRAM.RIGHT)
            targetTile = UTIL.calcTileFromPix([charPixRelative[0] + char.moveSpeed, charPixRelative[1]])
            if targetTile == charTileRelative:
                char.adjustPosition(char.moveSpeed, 0) 
            else:
                if self.borders[targetTile[1]][targetTile[0]] & 0b0100: #barrier in the way
                    char.adjustPosition(targetTile[0] * PRAM.TILESIZE - charPixRelative[0]-1, 0) #move next to barrier
                else:
                    char.adjustPosition(char.moveSpeed, 0)
                
#         self.game.gameScene.calcRenderChanges(char.actor, origin, targetTile, event.direction)
        char.actor.changed = True #flag to re-render the character                
        if char.actor.isFocus: #check if the camera needs to be adjusted
            self.game.gameCamera.panToChar(char.getPosition())
        
        if not self.game.gameCamera.moveFlag:
            self.game.renderer.addRenderBox_movedSprite(char.getSize(), origin, char.getPosition(), event.direction)
        
        if targetTile !=charTileRelative:  #Check if the targetTile tile has an event that triggers on touch
            targetTileTile = self.eventTiles.get((targetTile[1],targetTile[0]))
            if  targetTileTile is not None:
                if targetTileTile.levelEvent.trigger == PRAM.TRIG_TOUCH:
                    self.game.addEvent(targetTileTile.levelEvent.gameEvent)

        if len(char.moveListeners) > 0:
            self.game.addEvent(EventNotifyMove(event.character))
            
    def runDefaultAction(self, event):
        triggered = False
        char = event.character
        charPixRelative = UTIL.calcCharPix(char.getPosition(), char.getSize())
        charTileRelative = UTIL.calcTileFromPix(charPixRelative) #relative tile that char appears to stand on
        layout = self.game.gameScene.layoutWrapper.layout           
        
        if layout[charTileRelative[1]][charTileRelative[0]].levelEvent is not None: #check the space you are standing on
            if layout[charTileRelative[1]][charTileRelative[0]].levelEvent.trigger == PRAM.TRIG_ACTION:
                self.game.addEvent(layout[charTileRelative[1]][charTileRelative[0]].levelEvent.gameEvent)
                triggered = True
        
        elif char.actor.direction ==PRAM.UP: #now check the tile next to you that you are facing
            targetTile = UTIL.calcTileFromPix([charPixRelative[0],charPixRelative[1]-PRAM.TILESIZE])
            if layout[targetTile[1]][targetTile[0]].levelEvent is not None:
                if layout[targetTile[1]][targetTile[0]].levelEvent.trigger == PRAM.TRIG_ACTION:
                    self.game.addEvent(layout[targetTile[1]][targetTile[0]].levelEvent.gameEvent)
                    triggered = True
                
        elif char.actor.direction ==PRAM.DOWN:
            targetTile = UTIL.calcTileFromPix([charPixRelative[0], charPixRelative[1] + PRAM.TILESIZE])
            if layout[targetTile[1]][targetTile[0]].levelEvent is not None:
                if layout[targetTile[1]][targetTile[0]].levelEvent.trigger == PRAM.TRIG_ACTION:
                    self.game.addEvent(layout[targetTile[1]][targetTile[0]].levelEvent.gameEvent)
                    triggered = True    
                
        elif char.actor.direction ==PRAM.LEFT:
            targetTile = UTIL.calcTileFromPix([charPixRelative[0] - PRAM.TILESIZE, charPixRelative[1]])
            if layout[targetTile[1]][targetTile[0]].levelEvent is not None:
                if layout[targetTile[1]][targetTile[0]].levelEvent.trigger == PRAM.TRIG_ACTION:
                    self.game.addEvent(layout[targetTile[1]][targetTile[0]].levelEvent.gameEvent)
                    triggered = True
                                                                          
        else: # 'right'
            targetTile = UTIL.calcTileFromPix([charPixRelative[0] + PRAM.TILESIZE, charPixRelative[1]])
            if layout[targetTile[1]][targetTile[0]].levelEvent is not None:
                if layout[targetTile[1]][targetTile[0]].levelEvent.trigger == PRAM.TRIG_ACTION:
                    self.game.addEvent(layout[targetTile[1]][targetTile[0]].levelEvent.gameEvent)
                    triggered = True           
            
        if not triggered: #no level event, so perform characters default action
            self.game.addEvent(char.defaultAction())           
    
    def runNotifyMove(self, event):
        for listener in event.character.moveListeners:
            listenerEvent = listener.notify()
            if listenerEvent is not None:
                self.game.addEvent(listenerEvent)
    
    def runSound(self, event):
        self.game.soundPlayer.playSound(event.sound)   
    
    def runSong(self, event):
        self.game.musicPlayer.playSong(event.song)
    
    def runSetInput(self, event):
        self.game.inputHandler.setInputBehavior(event.inputType)    
    
    def runLoadLevel(self, event):
        self.game.loadLevel(event)          

    def runLoadMenu(self, event):
        self.game.loadMenu(event.menuFile)
    
    def runLoadCutscene(self, event):
        self.game.loadCutscene(event.cutsceneFile)
