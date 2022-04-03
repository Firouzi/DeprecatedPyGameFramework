from Game_Scene.Test.Mock_Classes.Grid_utility_mock import MockFlag
from Scene_Node.Render_node import SpriteNodeBase

class SpriteClone(SpriteNodeBase):
    def __init__(self, parent, is_visible, is_ethereal): #SpriteInstance
        super(SpriteClone, self).__init__(parent.entity_id)
        self.parent = parent
        #We are always sorted on the parent's ground position, regardless of cell or world position
        #self.ground_position = self.parent.particle.getPosition()
        self.ground_position = self.parent.getGroundPosition()
        self.has_changed = MockFlag(True) #flag is set if the render coordinates get updated
        self.image = self.parent.image
        self.is_ethereal = is_ethereal
        self.is_visible =  is_visible

    #When a sprite changes state, these methods are called to update the states of it's clones.
    #The clones are moved into the correct data structs within their cells.

    #Recursive method called on all clones
    #Updates the state and moves clone from linked list to invisibleTangible list
    def changeVisibleToInvisible(self):
        self.is_visible = False
        self.removeSelfFromLinkedList()
        self.cell.insertInvisibleTangibleNode(self)
        if self.horizontal_clone is not None:
            self.horizontal_clone.changeVisibleToInvisible()
        if self.vertical_clone is not None:
            self.vertical_clone.changeVisibleToInvisible()

    #Recursive method called on all clones
    #Updates the state and moves clone from invisibleTangible list to linked list
    def changeInvisibleToVisible(self):
        self.is_visible = True
        #self.cell.removeInvisibleTangibleNode(self.entity_id)
        self.removeSelfFromInvisibleLList()
        self.cell.insertNode(self)
        self.needs_sorting = True
        if self.horizontal_clone is not None:
            self.horizontal_clone.changeInvisibleToVisible()
        if self.vertical_clone is not None:
            self.vertical_clone.changeInvisibleToVisible()

    #Recursive method called on all clones, sets ethereal - this does not affect it's place in the cell
    def setEthereal(self):
        self.is_ethereal = True
        if self.horizontal_clone is not None:
            self.horizontal_clone.setEthereal()
        if self.vertical_clone is not None:
            self.vertical_clone.setEthereal()

    #Recursive method called on all clones, sets tangible - this does not affect it's place in the cell
    def setTangible(self):
        self.is_ethereal = False
        if self.horizontal_clone is not None:
            self.horizontal_clone.setTangible()
        if self.vertical_clone is not None:
            self.vertical_clone.setTangible()

    #Note, there is no use for an InvisibleEthereal clone

    def isActivated(self):
        return True

    def isVisible(self):
        return self.is_visible

    def isEthereal(self):
        return self.is_ethereal

    def setWorldPosition(self, world_position):
        self.world_position = world_position

    def parentSpriteNetworkHasChanged(self):
        return self.parent.parentSpriteNetworkHasChanged()

    def parentSpriteHasChanged(self):
        return self.parent.parentSpriteHasChanged()

    def parentSpriteIsAlwaysActive(self):
        return self.parent.parentSpriteIsAlwaysActive()

    def renderNetworkInActiveCell(self):
        return self.parent.renderNetworkInActiveCell()

    def addNetworkToOffscreenActive(self):
        self.parent.addNetworkToOffscreenActive()

    def removeNetworkFromOffscreenActive(self):
        self.parent.removeNetworkFromOffscreenActive()

    def notifyNetworkOffscreen(self):
        self.parent.notifyNetworkOffscreen()

    def notifyNetworkOnscreen(self):
        self.parent.notifyNetworkOnscreen()

    def setImageRenderCoordinates(self, image_render_coordinates):
        self.image_render_coordinates = image_render_coordinates
        self.has_changed.value = True

    def setCloneMoveFlags(self):
        self.needs_sorting = True
        if self.horizontal_clone is not None:
            self.horizontal_clone.setCloneMoveFlags()
        if self.vertical_clone is not None:
            self.vertical_clone.setCloneMoveFlags()

    #A Clone should call kill clones on it's clones (recursive kill), then remove self
    def killClones(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.killClones()
            self.horizontal_clone = None
        if self.vertical_clone is not None:
            self.vertical_clone.killClones()
            self.vertical_clone = None
        if self.isVisible():
            self.removeSelfFromLinkedList()
        else:
            self.removeSelfFromInvisibleLList()

    #called by an active cell
    #if the clone is visible, the return value is True if the clone needs to be sorted
    #this retVal can be ignored if the clone is invisible
    def updateNodeActive(self):
        if self.has_changed.value:
                self.image = self.parent.image
                self.updateRenderBorders()
        return self.needs_sorting

    def recursiveCloneUpdate(self):
        print("recursiveCloneUpdate called in SpriteClone base class, id: " + str(self.entity_id))
        assert False

    def updateRenderBorders(self):
        print("updateRenderBorders called in SpriteClone base class, id: " + str(self.entity_id))
        assert False

    ### CELL STATE CHANGES ###

    ###CHANGE CELL STATE FROM ACTIVE ###
    def cellStateActiveToInactive(self):
        #if there is not an incoming update for the parent sprite, and it is offscreen, notify
        if not self.renderNetworkInActiveCell():
            if not self.parentSpriteNetworkHasChanged() and not self.parentSpriteIsAlwaysActive():
                self.removeNetworkFromOffscreenActive()
                self.notifyNetworkOffscreen()

    ###CHANGE CELL STATE FROM INACTIVE ###
    #In this case, we may need to move a sprite to offscreen actives
    def cellStateInactiveToActive(self):
        self.addNetworkToOffscreenActive()
        self.notifyNetworkOnscreen()

class HorizontalSpriteClone(SpriteClone):
    def __init__(self, parent, is_visible, is_ethereal):
        super(HorizontalSpriteClone, self).__init__(parent, is_visible, is_ethereal)

    def cloneNetworkInActiveCell(self):
        if self.cellIsActive():
            return True
        if self.horizontal_clone is not None:
            if self.horizontal_clone.cloneNetworkInActiveCell():
                return True
        if self.vertical_clone is not None:
            if self.vertical_clone.cloneNetworkInActiveCell():
                return True
        return False

    def recursiveCloneUpdate(self):
        if self.has_changed.value:
            self.image = self.parent.image
            self.updateRenderBorders()
        if self.horizontal_clone is not None:
            self.horizontal_clone.recursiveCloneUpdate()
        if self.vertical_clone is not None:
            self.vertical_clone.recursiveCloneUpdate()

    def updateRenderBorders(self):
        #The render borders for this Clone are handled by the parent.
        #Check if another clone is needed, or needs to be removed
        if self.world_position[0] + self.image_render_coordinates[2] - 1 > self.cell.borders[2]:  # Right border
            #Adjust width of image to end at border of cell
            h_render_border = self.cell.size[0] #an h_clone with an h_clone will always have it's size be the entire cell
            #Check if world extends beyond right border of this cell
            if self.cell.borders[2] + 1 < self.grid.world_size[0]:
                if self.horizontal_clone is None:
                    self.horizontal_clone = HorizontalSpriteClone(self, self.isVisible(), self.isEthereal())
                    self.horizontal_clone.setWorldPosition([self.cell.borders[2]+1,
                                                            self.world_position[1]])
                    #If the horizonatal render coordinate goes over the next cell, the clone will create a clone
                    self.horizontal_clone.setImageRenderCoordinates([self.image_render_coordinates[0] + h_render_border,
                                                                     self.image_render_coordinates[1],
                                                                     self.image_render_coordinates[2] - h_render_border,
                                                                     self.image_render_coordinates[3]])
                    self.horizontal_clone.setGrid(self.grid)
                    self.horizontal_clone.setLayer(self.layer)
                    self.grid.insertHorizontalClone(self.horizontal_clone)
                else:
                    self.horizontal_clone.world_position[1] = self.world_position[1]
                    self.horizontal_clone.setImageRenderCoordinates([self.image_render_coordinates[0] + h_render_border,
                                                                     self.image_render_coordinates[1],
                                                                     self.image_render_coordinates[2] - h_render_border,
                                                                     self.image_render_coordinates[3]])
                    #if the cell is inactive, then the clone will not be updated this loop
                    # If the clone has been moved, it needs to be updated!
                    if not self.horizontal_clone.cell.isActive():
                        self.horizontal_clone.updateRenderBorders()
            #update the width of this image
            self.image_render_coordinates[2] = h_render_border
        #If not crossing border, may need to kill existing clone to the right
        elif self.horizontal_clone is not None:
            self.horizontal_clone.killClones() #this clone is removed from the LL, as well as it's clones
            self.horizontal_clone = None
        #See if crosses bottom border
        if self.world_position[1] + self.image_render_coordinates[3] - 1 > self.cell.borders[1]: #Bottom border
            #Adjust height of image to end at border of cell
            y_render_border = self.cell.borders[1] - self.world_position[1] + 1  # height
            # Check if world extends beyond top border of this cell
            if self.cell.borders[1] + 1 < self.grid.world_size[1]:
                if self.vertical_clone is None:
                    self.vertical_clone = VerticalSpriteClone(self, self.isVisible(), self.isEthereal())
                    self.vertical_clone.setWorldPosition([self.world_position[0],
                                                          self.cell.borders[1]+1])
                    self.vertical_clone.setImageRenderCoordinates([self.image_render_coordinates[0],
                                                                   self.image_render_coordinates[1] + y_render_border,
                                                                   self.image_render_coordinates[2],
                                                                   self.image_render_coordinates[3] - y_render_border])
                    self.vertical_clone.setGrid(self.grid)
                    self.vertical_clone.setLayer(self.layer)
                    self.grid.insertVerticalClone(self.vertical_clone)
                else:
                    #just need to update X component, Y is always remains border of the cell
                    self.vertical_clone.world_position[0] = self.world_position[0]
                    self.vertical_clone.setImageRenderCoordinates([self.image_render_coordinates[0],
                                                                   self.image_render_coordinates[1] + y_render_border,
                                                                   self.image_render_coordinates[2],
                                                                   self.image_render_coordinates[3] - y_render_border])
                    #if the cell is inactive, then the clone will not be updated this loop
                    # If the clone has been moved, it needs to be updated!
                    if not self.vertical_clone.cell.isActive():
                        self.vertical_clone.updateRenderBorders()
            # only render the main sprite up to the border
            self.image_render_coordinates[3] = y_render_border
        elif self.vertical_clone is not None:
            self.vertical_clone.killClones() #this clone is removed from the LL, as well as it's clones
            self.vertical_clone = None
        self.has_changed.value = False

#Only create vertical clones, not horizontal clones
class VerticalSpriteClone(SpriteClone):
    def __init__(self, parent, is_visible, is_ethereal):
        super(VerticalSpriteClone, self).__init__(parent, is_visible, is_ethereal)

    #overridden because vertical clones do not have horizontal clones
    def changeVisibleToInvisible(self):
        self.is_visible = False
        self.removeSelfFromLinkedList()
        self.cell.insertInvisibleTangibleNode(self)
        if self.vertical_clone is not None:
            self.vertical_clone.changeVisibleToInvisible()

    #overridden because vertical clones do not have horizontal clones
    def changeInvisibleToVisible(self):
        self.is_visible = True
        #self.cell.removeInvisibleTangibleNode(self.entity_id)
        self.removeSelfFromInvisibleLList()
        self.cell.insertNode(self)
        self.needs_sorting = True
        if self.vertical_clone is not None:
            self.vertical_clone.changeInvisibleToVisible()

    #Recursive method called on all clones, sets ethereal - this does not affect it's place in the cell
    def setEthereal(self):
        self.is_ethereal = True
        if self.vertical_clone is not None:
            self.vertical_clone.setEthereal()

    #Recursive method called on all clones, sets tangible - this does not affect it's place in the cell
    def setTangible(self):
        self.is_ethereal = False
        if self.vertical_clone is not None:
            self.vertical_clone.setTangible()

    def cloneNetworkInActiveCell(self):
        if self.cellIsActive():
            return True
        if self.vertical_clone is not None:
            if self.vertical_clone.cloneNetworkInActiveCell():
                return True
        return False

    #Vertical clones only create vertixcl clones
    def setCloneMoveFlags(self):
        self.needs_sorting = True
        if self.vertical_clone is not None:
            self.vertical_clone.setCloneMoveFlags()

    #Vertical clones only create vertical clones
    def killClones(self):
        if self.vertical_clone is not None:
            self.vertical_clone.killClones()
            self.vertical_clone = None
        if self.isVisible():
            self.removeSelfFromLinkedList()
        else:
            self.removeSelfFromInvisibleLList()

    def recursiveCloneUpdate(self):
        if self.has_changed.value:
            self.image = self.parent.image
            self.updateRenderBorders()
        if self.vertical_clone is not None:
            self.vertical_clone.recursiveCloneUpdate()

    #Does not check the horizontal border or create horizontal clones
    #Vertical portion is identical to the horizontalSpriteClone
    def updateRenderBorders(self):
        #See if crosses bottom border
        if self.world_position[1] + self.image_render_coordinates[3] - 1 > self.cell.borders[1]: #Bottom border
            #Adjust height of image to end at border of cell
            y_render_border = self.cell.size[1] #a clone with a clone will always have it's size be the entire cell
            # Check if world extends beyond top border of this cell
            if self.cell.borders[1] + 1 < self.grid.world_size[1]:
                if self.vertical_clone is None:
                    self.vertical_clone = VerticalSpriteClone(self, self.isVisible(), self.isEthereal())
                    self.vertical_clone.setWorldPosition([self.world_position[0],
                                                          self.cell.borders[1]+1])
                    self.vertical_clone.setImageRenderCoordinates([self.image_render_coordinates[0],
                                                                   self.image_render_coordinates[1] + y_render_border,
                                                                   self.image_render_coordinates[2],
                                                                   self.image_render_coordinates[3] - y_render_border])
                    self.vertical_clone.setGrid(self.grid)
                    self.vertical_clone.setLayer(self.layer)
                    self.grid.insertVerticalClone(self.vertical_clone)
                else:
                    #just need to update X component, Y is always remains border of the cell
                    self.vertical_clone.world_position[0] = self.world_position[0]
                    self.vertical_clone.setImageRenderCoordinates([self.image_render_coordinates[0],
                                                                   self.image_render_coordinates[1] + y_render_border,
                                                                   self.image_render_coordinates[2],
                                                                   self.image_render_coordinates[3] - y_render_border])
                    #if the cell is inactive, then the clone will not be updated this loop
                    # If the clone has been moved, it needs to be updated!
                    if not self.vertical_clone.cell.isActive():
                        self.vertical_clone.updateRenderBorders()
            # only render the main sprite up to the border
            self.image_render_coordinates[3] = y_render_border
        elif self.vertical_clone is not None:
            self.vertical_clone.killClones() #this clone is removed from the LL, as well as it's clones
            self.vertical_clone = None
        self.has_changed.value = False
