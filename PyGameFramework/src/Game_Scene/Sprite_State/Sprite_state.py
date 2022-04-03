from enum import Enum


class SpriteStateEnum(Enum):
    SPRITE_STATE_DEFAULT = 0 #Base class, do not instantiate
    SPRITE_STATE_ACTIVE = 1
    SPRITE_STATE_ACTIVE_INVISIBLE = 2
    SPRITE_STATE_ALWAYS_ACTIVE = 3
    SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE = 4
    SPRITE_STATE_DEACTIVATED_BASE = 5 #Base class, do not instantiate
    SPRITE_STATE_DEACTIVATED = 6
    SPRITE_STATE_INVISIBLE_DEACTIVATED = 7
    SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED = 8
    SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED = 9
    SPRITE_STATE_ACTIVE_ETHEREAL = 10
    SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL = 11
    SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL = 12
    SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL = 13
    SPRITE_STATE_ETHEREAL_DEACTIVATED = 14
    SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED = 15
    SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED = 16
    SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED = 17
    SPRITE_STATE_MAX = 18 #Sets the max value, do not instantiate

class SpriteState: #Base class
    def __init__(self):
        self.sprite_state_enum =  SpriteStateEnum.SPRITE_STATE_DEFAULT
        self.is_always_active =  False
        self.is_visible =  False
        self.is_activated = False
        self.is_ethereal = False
        #deactivating the sprite always does the same actions, only difference is the returned state
        #each active sprite state has a mirrored deactivated version
        #must set this after all states are defined
        self.deactivated_sprite_state = None

    #For the first time inserting a sprite into the grid
    def insertIntoGrid(self, sprite_node):
        print("insertIntoGrid called in SpriteState base class, id: " + str(sprite_node.entity_id))
        assert (1 == 2)

    def clearEntityDependancies(self, sprite_node):
        print("clearEntityDependancies called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def addEntityDependancy(self, sprite_node, dependant_node):
        print("addEntityDependancy called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def removeEntityDependancy(self, sprite_node, dependant_entity_id):
        print("removeEntityDependancy called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def isAlwaysActive(self):
        return self.is_always_active

    def parentSpriteHasChanged(self, sprite_node):
        print("parentSpriteHasChanged called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    ### CELL STATE CHANGES ###

    def cellStateActiveToInactive(self, sprite_node):
        return

    def cellStateInactiveToActive(self, sprite_node):
        return

    ### SPRITE STATE CHANGES ###

    def getSpriteStateEnum(self):
        return self.sprite_state_enum

    def deactivateSprite(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromLinkedList()
        sprite_node.removeNetworkFromOffscreenActive()
        sprite_node.cell = None
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        return self.deactivated_sprite_state

    def removeNode(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromLinkedList()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
        sprite_node.signalRemovedToDependants()
        sprite_node.cell = None #note this was added, don't think it would have much effect but feels cleaner

    def activateSprite(self, sprite_node):
        print("activateEntity called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    def setAlwaysActive(self, sprite_node):
        print("setAlwaysActive called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    def removeAlwaysActive(self, sprite_node):
        print("removeAlwaysActive called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    def setVisible(self, sprite_node):
        print("setVisible called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    def setInvisible(self, sprite_node):
        print("setInvisible called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    def setEthereal(self, sprite_node):
        print("setEthereal called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    def setTangible(self, sprite_node):
        print("setTangible called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)
    ### UPDATE ###

    #called by an active cell
    def updateNodeActive(self, sprite_node):
        print("updateNodeActive called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    #called by grid on any nodes in offscreen actives list
    #return TRUE if the node has moved into a new cell
    def updateNodeOffscreenActive(self, sprite_node):
        print("updateOffscreenActive called in SpriteState base class, id: "+ str(sprite_node.entity_id))
        assert(1==2)

#We only need 1 instance for each class, as they do not store state (state is stored in the node class)
SPRITE_STATE_ACTIVE = None
SPRITE_STATE_ACTIVE_INVISIBLE = None
SPRITE_STATE_ALWAYS_ACTIVE = None
SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE = None
SPRITE_STATE_ACTIVE_ETHEREAL = None
SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL = None
SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL = None
SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL = None

SPRITE_STATE_DEACTIVATED = None
SPRITE_STATE_INVISIBLE_DEACTIVATED = None
SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED = None
SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED = None
SPRITE_STATE_ETHEREAL_DEACTIVATED = None
SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED = None
SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED = None
SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED = None

