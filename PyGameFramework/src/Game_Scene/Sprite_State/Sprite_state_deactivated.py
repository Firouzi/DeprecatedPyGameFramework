import Sprite_state
from Sprite_state import SpriteState, SpriteStateEnum

class SpriteStateDeactivatedBase(SpriteState):
    def __init__(self):
        super(SpriteStateDeactivatedBase, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_DEACTIVATED_BASE
        self.is_always_active = False
        self.is_visible = True
        self.is_activated = False
        self.is_ethereal = False

    def removeNode(self, sprite_node):
        sprite_node.signalRemovedToDependants()

    #Deactivated sprites do not get inserted
    def insertIntoGrid(self, sprite_node):
        pass

    def parentSpriteHasChanged(self, sprite_node):
        print("parentSpriteHasChanged called in Deactivated base class, id: "+str(sprite_node.entity_id))
        assert(1==2)

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

    def activateSprite(self, sprite_node):
        print("activateEntity called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def setAlwaysActive(self, sprite_node):
        print("setAlwaysActive called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def removeAlwaysActive(self, sprite_node):
        print("removeAlwaysActive called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def setVisible(self, sprite_node):
        print("setVisible called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def setInvisible(self, sprite_node):
        print("setInvisible called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def setEthereal(self, sprite_node):
        print("setEthereal called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def setTangible(self, sprite_node):
        print("setTangible called in SpriteStateDeactivatedBase base class")
        assert(1==2)

    def updateNodeActive(self, sprite_node):
        print("updateNodeActive called on deactivated node, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def updateNodeInvisibleTrailLeft(self, sprite_node):
        print("updateNodeInvisibleTrailLeft called on deactivated node, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def updateNodeInvisibleTrailTop(self, sprite_node):
        print("updateNodeInvisibleTrailTop called on deactivated node, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def updateNodeInvisibleLeading(self, sprite_node):
        print("updateNodeInvisibleLeading called on deactivated node, id: "+ str(sprite_node.entity_id))
        assert(1==2)

    def updateNodeOffscreenActive(self, sprite_node):
        print("updateNodeOffscreenActive called on deactivated node, id: "+ str(sprite_node.entity_id))
        assert(1==2)

class SpriteStateDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_DEACTIVATED
        self.is_always_active = False
        self.is_visible = True
        self.is_activated = False
        self.is_ethereal = False

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
        sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        if sprite_node.renderNetworkInActiveCell():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ACTIVE

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

class SpriteStateInvisibleDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateInvisibleDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_INVISIBLE_DEACTIVATED
        self.is_always_active = False
        self.is_visible = False
        self.is_activated = False
        self.is_ethereal = False

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        if sprite_node.renderNetworkInActiveCell():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

class SpriteStateAlwaysActiveDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateAlwaysActiveDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED
        self.is_always_active = True
        self.is_visible = True
        self.is_activated = False
        self.is_ethereal = False

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
        sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        sprite_node.notifyNetworkOnscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

class SpriteStateAlwaysActiveInvisibleDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateAlwaysActiveInvisibleDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED
        self.is_always_active = True
        self.is_visible = False
        self.is_activated = False
        self.is_ethereal = False

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.grid.reinsertInvisibleTangibleNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        sprite_node.notifyNetworkOnscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED

class SpriteStateEtherealDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateEtherealDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ETHEREAL_DEACTIVATED
        self.is_always_active = False
        self.is_visible = True
        self.is_activated = False
        self.is_ethereal = True

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    #behavies the same as an active sprite
    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
        sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        if sprite_node.renderNetworkInActiveCell():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_DEACTIVATED

class SpriteStateInvisibleEtherealDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateInvisibleEtherealDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED
        self.is_always_active = False
        self.is_visible = False
        self.is_activated = False
        self.is_ethereal = True

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.grid.reinsertInvisibleEtherealNode(sprite_node)
        if sprite_node.renderNetworkInActiveCell():
            sprite_node.addNetworkToOffscreenActive()
            sprite_node.notifyNetworkOnscreen()
        else:
            sprite_node.removeNetworkFromOffscreenActive()
            sprite_node.notifyNetworkOffscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

class SpriteStateAlwaysActiveEtherealDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateAlwaysActiveEtherealDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED
        self.is_always_active = True
        self.is_visible = True
        self.is_activated = False
        self.is_ethereal = True

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.updateSpriteFrame()
        sprite_node.updateWorldPosition()
        sprite_node.needs_sorting = True
        sprite_node.grid.reinsertNode(sprite_node)
        sprite_node.updateRenderBorders()
        sprite_node.setCloneMoveFlags()
        sprite_node.recursiveCloneUpdate()
        sprite_node.addNetworkToOffscreenActive()
        sprite_node.notifyNetworkOnscreen()
        for dependant in sprite_node.dependant_sprite_nodes.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        for dependant in sprite_node.inactive_dependants.values():
            dependant.dependantSignalActive(sprite_node.entity_id)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED

class SpriteStateAlwaysActiveInvisibleEtherealDeactivated(SpriteStateDeactivatedBase):
    def __init__(self):
        super(SpriteStateAlwaysActiveInvisibleEtherealDeactivated, self).__init__()
        self.sprite_state_enum = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED
        self.is_always_active = True
        self.is_visible = False
        self.is_activated = False
        self.is_ethereal = True

    def deactivateSprite(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def activateSprite(self, sprite_node):
        sprite_node.grid.addToAlwaysActiveInvisibleEthereals(sprite_node)
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL

    def setAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def removeAlwaysActive(self, sprite_node):
        return Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setVisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED

    def setInvisible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setEthereal(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

    def setTangible(self, sprite_node):
        return Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED