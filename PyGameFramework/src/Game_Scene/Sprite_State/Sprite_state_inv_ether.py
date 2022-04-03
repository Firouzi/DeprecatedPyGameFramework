import Sprite_state
from Sprite_state import SpriteState, SpriteStateEnum

#These are kept in a dict in a cell.  They do not have clones,
#because they are not rendered or part of collisions
class SpriteStateInvisibleEthereal(SpriteState):
    def __init__(self):
        super(SpriteStateInvisibleEthereal, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL
        self.is_always_active =  False
        self.is_visible =  False
        self.is_activated = True
        self.is_ethereal = True

    def insertIntoGrid(self, sprite_node):
        sprite_node.grid.insertInvisibleEtherealNode(sprite_node)

    def parentSpriteHasChanged(self, sprite_node):
        if sprite_node.has_moved.value:
            return True
        return False

    def clearEntityDependancies(self, sprite_node):
        sprite_node.dependant_sprite_nodes = dict()
        sprite_node.inactive_dependants = dict()
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        if not sprite_node.cell.residesInCell(sprite_node.world_position):
            sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
            sprite_node.grid.reinsertInvisibleEtherealNode(sprite_node)
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
            sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
            sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
            sprite_node.grid.reinsertInvisibleEtherealNode(sprite_node)
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()

    ### SPRITE STATE CHANGES ###

    def deactivateSprite(self, sprite_node):
        sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
        sprite_node.removeNetworkFromOffscreenActive()
        sprite_node.cell = None
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        return self.deactivated_sprite_state

    def removeNode(self, sprite_node):
        sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)
        sprite_node.signalRemovedToDependants()

    def activateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
        sprite_node.cell = None
        sprite_node.grid.addToAlwaysActiveInvisibleEthereals(sprite_node)
        #effectively in 'inactive' sprite now, so signal all dependants
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalInactive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    def setVisible(self, sprite_node):
        sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
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
        return Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    def setTangible(self, sprite_node):
        sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
        sprite_node.grid.removeFromOffscreenActives(sprite_node.entity_id)  # in case it's in there
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
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
        sprite_node.setClonesTangible()
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
    #Active invisible nodes are a special case
        #Return TRUE if they have MOVED to a new cell
        #Return FALSE if they are still there

    #invisibleEthereal nodes do not update their image or behavior state, just their position
    def updateNodeActive(self, sprite_node):
        if sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position): #if we need to move to a new cell
                sprite_node.grid.moveInvisibleEtherealNode(sprite_node)  # will be inserted into a new cell, possibly updated
                return True #True means remove me from invisible_nodes
        return False #No Change

    def updateNodeOffscreenActive(self, sprite_node):
        if sprite_node.has_moved.value:
            sprite_node.updateWorldPosition()
            if not sprite_node.cell.residesInCell(sprite_node.world_position): #if we need to move to a new cell
                #This is OK to call here, the cell is not iterating through the invibible_nodes list at this point
                sprite_node.cell.removeInvisibleEtherealNode(sprite_node.entity_id)
                #Use reinsert instead of Move method to avoid offscreen active changes
                sprite_node.grid.reinsertInvisibleEtherealNode(sprite_node)  # will be inserted into a new cell, possibly updated
            if sprite_node.cellIsActive():
                return [sprite_node.entity_id] #means take me off of offscreen actives
            elif not sprite_node.renderNetworkInActiveCell() and not sprite_node.dependantNetworkHasChanged():
                sprite_node.notifyNetworkOffscreen()
                remove_ids = list()
                remove_ids.append(sprite_node.entity_id)
                remove_ids += sprite_node.getDependantIds()
                return remove_ids #means take me and the network off of offscreen actives
            else:
                return [] #no change
        return [] #no change