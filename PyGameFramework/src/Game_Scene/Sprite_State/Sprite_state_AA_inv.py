import Sprite_state
from Sprite_state import SpriteState, SpriteStateEnum

#These sprites are kept in a list in a Cell (not a linked list), as they are no rendered
#But they do have clones as they participate in collisions
class SpriteStateAlwaysActiveInvisible(SpriteState):
    def __init__(self):
        super(SpriteStateAlwaysActiveInvisible, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE
        self.is_always_active =  True
        self.is_visible =  False
        self.is_activated = True
        self.is_ethereal = False

    def insertIntoGrid(self, sprite_node):
        sprite_node.grid.insertAlwaysActiveInvisibleTangibleNode(sprite_node)

    def parentSpriteHasChanged(self, sprite_node):
        if sprite_node.has_moved.value or sprite_node.animation_has_flipped.value or sprite_node.state_has_changed.value:
            return True
        return False

    def clearEntityDependancies(self, sprite_node):
        sprite_node.dependant_sprite_nodes = dict()
        sprite_node.inactive_dependants = dict()

    def addEntityDependancy(self, sprite_node, dependant_node):
        sprite_node.dependant_sprite_nodes[dependant_node.entity_id] = dependant_node
        sprite_node.addNetworkToOffscreenActive()

    def removeEntityDependancy(self, sprite_node, dependant_entity_id):
        try:
            del(sprite_node.dependant_sprite_nodes[dependant_entity_id])
        except:
            pass

    def removeNode(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromInvisibleLList()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
        sprite_node.cell = None
        sprite_node.signalRemovedToDependants()

    ### SPRITE STATE CHANGES ###

    def deactivateSprite(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromInvisibleLList()
        sprite_node.removeNetworkFromOffscreenActive()
        sprite_node.cell = None
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        return self.deactivated_sprite_state

    def activateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    def removeAlwaysActive(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):  # if we need to move to a new cell
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id) #in case it's in there
            sprite_node.killClones()  # recursively kills the clones for this sprite instance
            sprite_node.resetRenderCoordinates()
            sprite_node.removeSelfFromInvisibleLList()
            sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)  # will be inserted into a new cell, possibly updated
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE

    def setVisible(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromInvisibleLList()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
        sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        sprite_node.clonesInvisibleToVisible()
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    #Ethereal and active sprites behave the same - ethereal sprites won't be included in collision detection however
    def setEthereal(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromInvisibleLList()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
        sprite_node.cell = None
        sprite_node.grid.addToAlwaysActiveInvisibleEthereals(sprite_node)
        # effectively in 'inactive' sprite now, so signal all dependants
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    ### CELL STATE CHANGES ###
        ###CHANGE CELL STATE FROM ACTIVE ###
    def cellStateActiveToInactive(self, sprite_node):
        sprite_node.grid.addToOffscreenActives(sprite_node)

        ###CHANGE CELL STATE FROM INACTIVE ###
    def cellStateInactiveToActive(self, sprite_node):
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)

    ### UPDATE ###

    #called by an active cell
    def updateNodeActive(self, sprite_node):
        if sprite_node.updateSpriteFrame() or sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position): #if we need to move to a new cell
                sprite_node.killClones()  # recursively kills the clones for this sprite instance
                sprite_node.resetRenderCoordinates()
                sprite_node.removeSelfFromInvisibleLList()
                sprite_node.grid.moveAlwaysActiveInvisibleNode(sprite_node)  # will be inserted into a new cell, possibly updated
                return False
            sprite_node.updateRenderBorders() #sets a flag in any clones so that they update their borders
            sprite_node.setCloneMoveFlags()
        return False

    #We cannot directly change the offscreen actives dict here, because it is in the process of being updated
    #If the node moves cells, we send an update enum to the caller (the grid) so that it will update its dict
    def updateNodeOffscreenActive(self, sprite_node):
        if sprite_node.updateSpriteFrame() or sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position):  # if we need to move to a new cell
                sprite_node.killClones()  # recursively kills the clones for this sprite instance
                sprite_node.resetRenderCoordinates()
                sprite_node.removeSelfFromInvisibleLList()
                sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)  # will be inserted into a new cell, possibly updated
                if sprite_node.cellIsActive():
                    sprite_node.has_moved.value = True  # Force an update when we get to this cell/node
                    return [sprite_node.entity_id] #means remove me from offscreen actives
                else:
                    sprite_node.updateRenderBorders()
                    return [] #no change
            else:  # if it is re-inserted into a new cell, sort()/updateSprite() are called as needed
                sprite_node.updateRenderBorders()  # sets a flag in any clones so that they update their borders
                sprite_node.setCloneMoveFlags()
                sprite_node.recursiveCloneUpdate()
        return [] #no change