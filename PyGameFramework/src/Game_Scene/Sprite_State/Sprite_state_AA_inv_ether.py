import Sprite_state
from Sprite_state import SpriteState, SpriteStateEnum

#This is a special case where we do not even store this sprite in a cell in the grid
#Keep it in a list of of SpriteStateAlwaysActiveInvisibleEthereals, because we always
#Update this sprite, but it does not interact (no collisions, do clones)
class SpriteStateAlwaysActiveInvisibleEthereal(SpriteState):
    def __init__(self):
        super(SpriteStateAlwaysActiveInvisibleEthereal, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL
        self.is_always_active =  True
        self.is_visible =  False
        self.is_activated = True
        self.is_ethereal = True

    def insertIntoGrid(self, sprite_node):
        sprite_node.grid.addToAlwaysActiveInvisibleEthereals(sprite_node)

    def parentSpriteHasChanged(self, sprite_node):
        if sprite_node.has_moved.value:
            return True
        return False

    def clearEntityDependancies(self, sprite_node):
        sprite_node.dependant_sprite_nodes = dict()
        sprite_node.inactive_dependants = dict()

    def addEntityDependancy(self, sprite_node, dependant_node):
        sprite_node.inactive_dependants[dependant_node.entity_id] = dependant_node

    def removeEntityDependancy(self, sprite_node, dependant_entity_id):
        try:
            del(sprite_node.inactive_dependants[dependant_entity_id])
        except:
            pass

    #we don't need to do anything here, we are already removed from any cell
    def deactivateSprite(self, sprite_node):
        sprite_node.grid.removeFromAlwaysActiveInvisibleEthereals(sprite_node.entity_id)
        return self.deactivated_sprite_state

    def removeNode(self, sprite_node):
        sprite_node.grid.removeFromAlwaysActiveInvisibleEthereals(sprite_node.entity_id)
        sprite_node.signalRemovedToDependants()

    def activateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    def removeAlwaysActive(self, sprite_node):
        sprite_node.grid.removeFromAlwaysActiveInvisibleEthereals(sprite_node.entity_id)
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        #always active invisible sprites are not in a cell
        sprite_node.grid.reinsertInvisibleEtherealNode(sprite_node)
        if sprite_node.renderNetworkInActiveCell() or sprite_node.parentSpriteHasChanged():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        #signals that this sprite is now active
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    def setVisible(self, sprite_node):
        sprite_node.grid.removeFromAlwaysActiveInvisibleEthereals(sprite_node.entity_id)
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
        sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        sprite_node.notifyNetworkOnscreen()
        sprite_node.clonesInvisibleToVisible()
        #signals that this sprite is now active
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    def setTangible(self, sprite_node):
        sprite_node.grid.removeFromAlwaysActiveInvisibleEthereals(sprite_node.entity_id)
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        sprite_node.notifyNetworkOnscreen()
        # signals that this sprite is now active
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        sprite_node.setClonesTangible()
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    #We don't need to update the AA_Inv_Ether nodes in the scene manager

    #called by an active cell
    def updateNodeActive(self, sprite_node):
        print("updateNodeActive called in SpriteStateAlwaysActiveInvisibleEthereal, id: " + str(sprite_node.entity_id))
        assert(1==2)

    #called by an invisible trail left cell
    def updateNodeInvisibleTrailLeft(self, sprite_node):
        print("updateNodeInvisibleTrailLeft called in SpriteStateAlwaysActiveInvisibleEthereal, id: " + str(sprite_node.entity_id))
        assert(1==2)

    #called by an invisible trail top cell
    def updateNodeInvisibleTrailTop(self, sprite_node):
        print("updateNodeInvisibleTrailTop called in SpriteStateAlwaysActiveInvisibleEthereal, id: " + str(sprite_node.entity_id))
        assert(1==2)

    #called by an invisible leading cell
    def updateNodeInvisibleLeading(self, sprite_node):
        print("updateNodeInvisibleLeading called in SpriteStateAlwaysActiveInvisibleEthereal, id: " + str(sprite_node.entity_id))
        assert(1==2)

    def updateNodeOffscreenActive(self, sprite_node):
        print("updateNodeOffscreenActive called in SpriteStateAlwaysActiveInvisibleEthereal, id: " + str(sprite_node.entity_id))
        assert(1==2)