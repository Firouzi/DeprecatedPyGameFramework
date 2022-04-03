import utility as UTIL
import parameters as PRAM

class GameCamera:
    def __init__(self, position = (0,0), tile = (0,0), offset = (0,0), maxPosition = (0,0)):
        self.position = position #absolute pixel position of the top left corner of camera
        self.tile = tile #tile position of top left corner of camera
        self.offset = offset  #pixels that camera is offset from the boundry of the tile
        self.maxPosition = maxPosition #don't pan further than this coordinate 
        
        self.moveFlag = True #set true when the camera has move, means re-render the entire screen
        
    def getPosition(self):
        return self.position
    
    def getTile(self):
        return self.tile
        
    def getOffset(self):
        return self.offset    
        
    def setPosition(self, position = (0,0)):
        self.position = position
        if self.position[0] < 0:
            self.position[0] = 0
        if self.position[1] < 0:
            self.position[1] = 0
        if self.position[0] > self.maxPosition[0]:
            self.position[0] = self.maxPosition[0]
        if self.position[1] > self.maxPosition[1]:
            self.position[1] = self.maxPosition[1]
             
        self.tile = UTIL.calcTileFromPix(self.position)
        self.offset = (self.position[0] - (self.tile[0] *PRAM.TILESIZE), self.position[1] - (self.tile[1] *PRAM.TILESIZE) )
        
    def adjustPosition(self, xChange, yChange):
        self.setPosition([self.position[0] + xChange, self.position[1] + yChange])
        
    def panToChar(self, charPosition):
        origin = self.position[:]
        
        if charPosition[0] - self.position[0] < PRAM.CAMERA_WIDTH:
            xChange = charPosition[0] - self.position[0] - PRAM.CAMERA_WIDTH 
        elif charPosition[0] - self.position[0] > PRAM.DISPLAY_WIDTH - PRAM.CAMERA_WIDTH:
            xChange = (charPosition[0] - self.position[0]) - (PRAM.DISPLAY_WIDTH - PRAM.CAMERA_WIDTH)
        else:
            xChange = 0
        
        if charPosition[1] - self.position[1] < PRAM.CAMERA_HEIGHT:
            yChange = charPosition[1] - self.position[1] - PRAM.CAMERA_HEIGHT
        elif charPosition[1] - self.position[1] > PRAM.DISPLAY_HEIGHT - PRAM.CAMERA_HEIGHT:
            yChange = (charPosition[1] - self.position[1]) - (PRAM.DISPLAY_HEIGHT- PRAM.CAMERA_HEIGHT)
        else:
            yChange = 0
            
        if xChange != 0 or yChange != 0:
            self.adjustPosition(xChange, yChange)
            
        if origin != self.position: #if camera actually moved, set the flag so the screen re-renders
            self.moveFlag = True

    
            