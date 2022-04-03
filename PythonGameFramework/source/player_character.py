import parameters as PRAM

# Class to contain data and actions for a PC.  Actions are added to the object
#     and modified dynamically
# @param actor
class PlayerCharacter:
    def __init__(self, actor = None):
        self.actor = actor #link to the actor player is controlling
                
        #explicitly declare fields
        self.moveSpeed = 10
        self.moveListeners = [] #to check for events generated by touch
        
    def addListener(self, listenerType, listener):
        if listenerType == PRAM.LISTENER_MOVE:
            self.moveListeners.append(listener)

    def adjustPosition(self, xChange, yChange):
        pos = self.getPosition()
        self.setPosition([pos[0] + xChange, pos[1] + yChange])
        
    def getPosition(self):
        return self.actor.getPosition()
    
    def setPosition(self, position):
        self.actor.setPosition(position)
    
    def getSize(self):
        return self.actor.size
    
    def setDirection(self, direction):
        self.actor.direction = direction
        