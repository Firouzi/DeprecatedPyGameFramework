import Sprite_state
from Sprite_state import SpriteState, SpriteStateEnum

#An ethereal sprite behaves the same as a normal active sprite as far as grid/cells are concerned
#They will be ignored for collision detections
class SpriteStateEthereal(SpriteState):
    def __init__(self):
        super(SpriteStateEthereal, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ACTIVE_ETHEREAL
        self.is_always_active =  False
        self.is_visible =  True
        self.is_activated = True
        self.is_ethereal = True

    def insertIntoGrid(self, sprite_node):
        sprite_node.grid.insertActiveNode(sprite_node)

    def parentSpriteHasChanged(self, sprite_node):
        if sprite_node.has_moved.value or sprite_node.animation_has_flipped.value or sprite_node.state_has_changed.value:
            return True
        return False

    #If the sprite has moved, it may create clones in an active cell
    #Therefore must first update position before checking for active cell
    def clearEntityDependancies(self, sprite_node):
        sprite_node.dependant_sprite_nodes = dict()
        sprite_node.inactive_dependants = dict()
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):
            sprite_node.killClones()  # recursively kills the clones for this sprite instance
            sprite_node.resetRenderCoordinates()
            sprite_node.removeSelfFromLinkedList()  # updates all of the pointers for this linked list
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
            sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()

    def addEntityDependancy(self, sprite_node, dependant_node):
        sprite_node.dependant_sprite_nodes[dependant_node.entity_id] = dependant_node
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()

    def removeEntityDependancy(self, sprite_node, dependant_entity_id):
        try:
            del(sprite_node.dependant_sprite_nodes[dependant_entity_id])
        except:
            pass
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):
            sprite_node.killClones()  # recursively kills the clones for this sprite instance
            sprite_node.resetRenderCoordinates()
            sprite_node.removeSelfFromLinkedList()  # updates all of the pointers for this linked list
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
            sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()

    ### SPRITE STATE CHANGES ###

    def activateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
            sprite_node.killClones()  # recursively kills the clones for this sprite instance
            sprite_node.resetRenderCoordinates()
            sprite_node.removeSelfFromLinkedList()  # updates all of the pointers for this linked list
            sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        #setting always active already notifies we are onscreen
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL

    def setInvisible(self, sprite_node):
        #after killing clones, there may not be any part of the sprite network in an active cell
        sprite_node.killClones()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
        sprite_node.removeSelfFromLinkedList() #Linked List is only for visible sprites
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.grid.reinsertInvisibleEtherealNode(sprite_node)
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    #Ethereal and active sprites behave the same - ethereal sprites won't be included in collision detection however
    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL

    #Really no change in behavior here
    def setTangible(self, sprite_node):
        sprite_node.setClonesTangible()
        return Sprite_state.SPRITE_STATE_ACTIVE

    ### CELL STATE CHANGES ###

    #If the network has a change, push it to offscreen actives
    #The full update will be made during updateNodeOffscreenActive
    def cellStateActiveToInactive(self, sprite_node):
        if sprite_node.parentSpriteNetworkHasChanged() or sprite_node.renderNetworkInActiveCell():
            sprite_node.addNetworkToOffscreenActive()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()

    def cellStateInactiveToActive(self, sprite_node):
        #if this returns False, that means the entity was not in offscreen inactives
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
        #if the sprite_node wasn't in offscreen actives, it was not ofscreen, and is now onscreen
        sprite_node.grid.notifySpriteOnscreen(sprite_node.entity_id)
        #any dependants that are in inactive cells will be moved to offscreen actives, and EM will be notified
        sprite_node.addDependantsToOffscreenActiveAndNotify()

    ### UPDATE SPRITE ###

    #Return the value of the move flag.  The cell sort/set clone move flags as needed
    #called by an active cell
    def updateNodeActive(self, sprite_node):
        if sprite_node.updateSpriteFrame() or sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position): #if we need to move to a new cell
                sprite_node.killClones()  # recursively kills the clones for this sprite instance
                sprite_node.resetRenderCoordinates()
                sprite_node.removeSelfFromLinkedList()  # updates all of the pointers for this linked list
                sprite_node.grid.moveActiveNode(sprite_node)  # will be inserted into a new cell, possibly updated
                return False #False means 'don't sort me'
            sprite_node.updateRenderBorders() #sets a flag in any clones so that they update their borders
            sprite_node.setCloneMoveFlags()
        return sprite_node.needs_sorting

    #We cannot directly change the offscreen actives dict here, because it is in the process of being updated
    #Return any entity ids that should be removed from offscreen actives
    def updateNodeOffscreenActive(self, sprite_node):
        if sprite_node.updateSpriteFrame() or sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position):  # if we need to move to a new cell
                sprite_node.killClones()  # recursively kills the clones for this sprite instance
                sprite_node.resetRenderCoordinates()
                sprite_node.removeSelfFromLinkedList()  # updates all of the pointers for this linked list
                #Use the reinsert method rather than the move method to avoid offscreen active changes
                sprite_node.grid.reinsertNode(sprite_node)
            sprite_node.updateRenderBorders()
            sprite_node.setCloneMoveFlags()
            sprite_node.recursiveCloneUpdate()
            if sprite_node.cellIsActive():
                return [sprite_node.entity_id] #pull this out of the offscreen actives list
            elif not sprite_node.renderNetworkInActiveCell() and not sprite_node.dependantNetworkHasChanged():
                sprite_node.notifyNetworkOffscreen()
                remove_ids = list()
                remove_ids.append(sprite_node.entity_id)
                remove_ids += sprite_node.getDependantIds()
                return remove_ids #means take me and the network off of offscreen actives
            else:
                return [] #no change
        return [] #no change
