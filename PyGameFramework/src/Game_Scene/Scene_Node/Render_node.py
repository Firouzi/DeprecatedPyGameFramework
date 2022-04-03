from Scene_Node.Scene_node import SceneNode

#This class is meant to be extended by specific renderable types of nodes
class RenderNode(SceneNode):
    def __init__(self, entity_id):
        super(RenderNode, self).__init__(entity_id)

        #Since we may need to clip the image accoarding to the size of the cell, we need to store the result here
        #Need this in combination with the world_position to blit the image
        self.image_render_coordinates = [0,0,0,0] #Calculated by the Sprite. X,Y,W,H

    def updateRenderBorders(self):
        print("updateRenderBorders called in RenderNode base class, id: " + str(self.entity_id))
        assert False

    #Overridden in sprite, checking the sprite state
    def isVisible(self):
        print("isVisible called in RenderNode base class, id: " + str(self.entity_id))
        assert False

    def isEthereal(self):
        print("isTangible called in RenderNode base class, id: " + str(self.entity_id))
        assert False

    def renderNetworkInActiveCell(self):
        print("renderNetworkInActiveCell called in RenderNode base class, id: " + str(self.entity_id))
        assert False

class TileNode(RenderNode):
    def __init__(self, entity_id):
        super(TileNode, self).__init__(entity_id)

#This class is meant to be extended by types of SpriteNodes
class SpriteNodeBase(RenderNode):
    def __init__(self, entity_id):
        super(SpriteNodeBase, self).__init__(entity_id)

    def parentSpriteNetworkHasChanged(self):
        print("parentSpriteNetworkHasChanged called in SpriteNodeBase base class, id: " + str(self.entity_id))
        assert False

    def parentSpriteHasChanged(self):
        print("parentSpriteHasChanged called in SpriteNodeBase base class, id: " + str(self.entity_id))
        assert False

    def parentSpriteIsAlwaysActive(self):
        print("parentSpriteIsAlwaysActive called in SpriteNodeBase base class, id: " + str(self.entity_id))
        assert False
