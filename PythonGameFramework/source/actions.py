import parameters as PRAM
from event import EventSound, EventMove

class ActionBase:
    def __init__(self,character,params=()):
        self.character=character
        self.params=params

    def act(self, params=()):
        return ''

class ActionMove(ActionBase):
    def __init__(self, character, params=()):
        super(ActionMove, self).__init__(character, params)
    
    def act(self, direction=()):
        return EventMove(self.character, direction)


class ActionColorSwap(ActionBase):
    def __init__(self, character, params = ()):   
        super(ActionColorSwap, self).__init__(character, params)
    
    def act(self, params=()):
        self.character.actor.colorSwap()
        self.character.actor.changed = True #re-render
        return EventSound(PRAM.SOUND_COLORSWAP)      
        
        
        
        
        