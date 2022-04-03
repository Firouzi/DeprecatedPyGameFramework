from event import EventLoadLevel, EventLoadMenu, EventDefaultAction
import parameters as PRAM

class ButtonMap:
    def __init__(self, 
                 up = PRAM.INPUT_UP, 
                 down = PRAM.INPUT_DOWN, 
                 left =  PRAM.INPUT_LEFT, 
                 right = PRAM.INPUT_RIGHT, 
                 action = PRAM.INPUT_ACTION,
                 status = PRAM.INPUT_STATUS,
                 enterDebug = PRAM.INPUT_DEBUG,
                 ):
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.action = action
        self.status = status
        self.enterDebug = enterDebug

class InputHandler:
    def __init__(self, game = None, player = None, buttonMap = None, inputType = PRAM.INPTYPE_OBSERVER):
        self.game = game
        self.player = player
        self.buttonMap = buttonMap

        self.inputUpBehavior = None
        self.inputDownBehavior = None
        self.inputLeftBehavior = None
        self.inputRightBehavior = None
        self.inputActionBehavior = None
        self.inputCancelBehavior = None
        self.inputStatusBehavior = None
        self.leftClickBehavior = None
        self.enterDebugBehavior = None

        self.setInputBehavior(inputType)
      
    def handleInputs(self):
        while len(self.game.keydownEvents) > 0:
            event = self.game.keydownEvents.pop()
            if event.type == PRAM.KEYDOWN:
                if event.key == self.buttonMap.action:
                    self.inputActionBehavior()
                elif event.key == self.buttonMap.status:
                    self.inputStatusBehavior()
                elif event.key == self.buttonMap.enterDebug:
                    self.enterDebugBehavior()
            elif event.type == PRAM.CLICKDOWN:
                if event.button == PRAM.INPUT_LEFTCLICK:
                    self.leftClickBehavior(event.pos)
            #Add more key events here
        
        #check which keys are currently pressed down        
        if self.game.keysPressed[self.buttonMap.up]:
            self.inputUpBehavior()
        if self.game.keysPressed[self.buttonMap.down]:
            self.inputDownBehavior()
        if self.game.keysPressed[self.buttonMap.left]:
            self.inputLeftBehavior()
        if self.game.keysPressed[self.buttonMap.right]:
            self.inputRightBehavior()
        
        return

    def setInputBehavior(self, inputType):
        if inputType == PRAM.INPTYPE_OBSERVER:
            self.inputUpBehavior = self.doNothing
            self.inputDownBehavior = self.doNothing
            self.inputLeftBehavior = self.doNothing
            self.inputRightBehavior = self.doNothing
            self.inputActionBehavior = self.doNothing
            self.inputCancelBehavior = self.doNothing
            self.inputStatusBehavior = self.doNothing
            self.leftClickBehavior = self.printPixelPosition

        elif inputType == PRAM.INPTYPE_MENU:
            self.inputUpBehavior = self.menuUp
            self.inputDownBehavior = self.menuDown
            self.inputLeftBehavior = self.menuLeft
            self.inputRightBehavior = self.menuRight
            self.inputActionBehavior = self.menuAction 
            self.inputCancelBehavior = self.menuCancel
            self.inputStatusBehavior = self.doNothing
            self.leftClickBehavior = self.printPixelPosition

        elif inputType == PRAM.INPTYPE_NORMAL:        
            self.inputUpBehavior = self.movementUp
            self.inputDownBehavior = self.movementDown
            self.inputLeftBehavior = self.movementLeft
            self.inputRightBehavior = self.movementRight
            self.inputActionBehavior = self.defaultAction 
            self.inputCancelBehavior = self.doNothing
            self.inputStatusBehavior = self.statusAction
            self.enterDebugBehavior = self.startDebug
            self.leftClickBehavior = self.printPixelPosition

    def movementUp(self):
        self.game.addEvent(self.player.actionMove(PRAM.UP))
        
    def movementDown(self):
        self.game.addEvent(self.player.actionMove(PRAM.DOWN))
    
    def movementLeft(self):
        self.game.addEvent(self.player.actionMove(PRAM.LEFT))
    
    def movementRight(self):
        self.game.addEvent(self.player.actionMove(PRAM.RIGHT))
    
    def defaultAction(self):
        self.game.addEvent(EventDefaultAction(self.player)) #'default behavior'
    
    def statusAction(self):
        self.game.addEvent(EventLoadMenu(PRAM.MENU_TEST1)) #TODO temp code to test menu/level load       
    
    def menuUp(self):
        pass

    def menuDown(self):
        pass

    def menuLeft(self):
        pass
    
    def menuRight(self):
        pass

    def menuAction(self):
        self.game.addEvent(EventLoadLevel(3, [250,350])) #TODO temp code to test menu/level load
    
    def menuCancel(self):
        pass
   
    def doNothing(self):
        pass

    def startDebug(self):
        self.game.runDebug = True

    def printPixelPosition(self, args):  #prints the coordinates of the mouse click
        click_x = args[0]
        click_y = args[1]
        abs_x = click_x + self.game.gameCamera.tile[0]*PRAM.TILESIZE + self.game.gameCamera.offset[0]
        abs_y = click_y + self.game.gameCamera.tile[1]*PRAM.TILESIZE + self.game.gameCamera.offset[1]
        print('\nRelative: ('+str(click_x)+','+str(click_y)+')')
        print('Absolute: ('+str(abs_x)+','+str(abs_y )+')')