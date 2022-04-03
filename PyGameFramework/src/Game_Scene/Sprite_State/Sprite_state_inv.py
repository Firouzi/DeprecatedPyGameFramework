import Sprite_state
from Sprite_state import SpriteState, SpriteStateEnum

#Kept in a list of tangible nodes in a cell, aren't displayed and don't need to be sorted
#Do have clones, because they are checked for collisions
class SpriteStateActiveInvisible(SpriteState):
    def __init__(self):
        super(SpriteStateActiveInvisible, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE
        self.is_always_active =  False
        self.is_visible =  False
        self.is_activated = True
        self.is_ethereal = False

    def insertIntoGrid(self, sprite_node):
        sprite_node.grid.insertInvisibleTangibleNode(sprite_node)

    def parentSpriteHasChanged(self, sprite_node):
        if sprite_node.has_moved.value or sprite_node.animation_has_flipped.value or sprite_node.state_has_changed.value:
            return True
        return False

    def clearEntityDependancies(self, sprite_node):
        sprite_node.dependant_sprite_nodes = dict()
        sprite_node.inactive_dependants = dict()
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):
            sprite_node.killClones()  # recursively kills the clones for this sprite instance
            sprite_node.resetRenderCoordinates()
            sprite_node.removeSelfFromInvisibleLList()
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
            sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
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
            sprite_node.removeSelfFromInvisibleLList()
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
            sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
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

    def removeNode(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromInvisibleLList()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
        sprite_node.cell = None
        sprite_node.signalRemovedToDependants()

    def activateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE

    def setAlwaysActive(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
            sprite_node.killClones()  # recursively kills the clones for this sprite instance
            sprite_node.resetRenderCoordinates()
            sprite_node.removeSelfFromInvisibleLList()
            sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive() #only done if cell is inactive
        #setting always active already notifies we are onscreen
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    def removeAlwaysActive(self, sprite_node):
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
        sprite_node.clonesInvisibleToVisible()
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        return Sprite_state.SPRITE_STATE_ACTIVE

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE

    def setEthereal(self, sprite_node):
        sprite_node.killClones()
        sprite_node.removeSelfFromInvisibleLList()
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
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

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE

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
        # if this returns False, that means the entity was not in offscreen inactives
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
        # if the sprite_node wasn't in offscreen actives, it was not onscreen, and is now onscreen
        sprite_node.grid.notifySpriteOnscreen(sprite_node.entity_id)
        # any dependants that are in inactive cells will be moved to offscreen actives, and EM will be notified
        sprite_node.addDependantsToOffscreenActiveAndNotify()

    ### UPDATE SPRITE ###

    def updateNodeActive(self, sprite_node):
        if sprite_node.updateSpriteFrame() or sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position): #if we need to move to a new cell
                sprite_node.killClones()  # recursively kills the clones for this sprite instance
                sprite_node.resetRenderCoordinates()
                sprite_node.removeSelfFromInvisibleLList()
                sprite_node.grid.moveInvisibleTangibleNode(sprite_node)  # will be inserted into a new cell, possibly updated
                return False
            sprite_node.updateRenderBorders() #sets a flag in any clones so that they update their borders
            sprite_node.setCloneMoveFlags()
        return False #Stays in the cell

    def updateNodeOffscreenActive(self, sprite_node):
        if sprite_node.updateSpriteFrame() or sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position):  # if we need to move to a new cell
                sprite_node.killClones()  # recursively kills the clones for this sprite instance
                sprite_node.resetRenderCoordinates()
                sprite_node.removeSelfFromInvisibleLList()
                #Use the reinsert method rather than the move method to avoid offscreen active changes
                sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
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