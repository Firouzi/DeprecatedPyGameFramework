from Scene_Node.Render_node import SpriteNodeBase
from Scene_Node.Clone_node import VerticalSpriteClone, HorizontalSpriteClone

class SpriteNode(SpriteNodeBase):
    def __init__(self,
                 entity_id, #int
                 particle, #Particle
                 behaviorFSM, #BehaviorFSM
                 state_images, #dict
                 state_image_coordinate_lists, #dict of coordinate lists
                 initial_sprite_state): #SpriteState (child of)
        super(SpriteNode, self).__init__(entity_id)
        self.particle = particle
        self.behaviorFSM = behaviorFSM
        #When we have a behavior state change, we return the associated image and coordinate set.
        #One potential optimization is for any sprite that has multiple behavior states corresponding to the
        #same sprite, we can choose 1 behavior state ID to send over from behaviorComponent to act as te representative
        #behavior ID for all of these.  This will not only make for less copies stored in these structs, it will make
        #the has_changed value be true ONLY when the behavior change changes the animation
        #for each behavior state, image tied to the behavior state id
        self.state_images = state_images
        self.image = None
        #for each behavior state, image tied to the behavior state id
        self.state_image_coordinate_lists = state_image_coordinate_lists

        #initialize the state (will be updated on first render)
        self.behavior_state_id =self.behaviorFSM.getBehaviorState() #current behavior state
        self.image_coordinates_list = self.state_image_coordinate_lists[self.behavior_state_id]
        self.frame = self.behaviorFSM.frame #current frome
        self.image_coordinates = self.image_coordinates_list[self.frame] #The current portion of the current image

        self.animation_has_flipped = self.behaviorFSM.animation_has_flipped
        self.state_has_changed = self.behaviorFSM.state_has_changed
        self.has_moved = self.particle.has_moved #shared ref

        #initialize
        self.current_sprite_state = initial_sprite_state
        self._setPositionPtr() #set position pointer
        #If a SpriteInstance has either clones or dependant_sprites (or their clones) in active cells
        #they must continue to be updated even if not within an active cell (in offscreen actives)
        #Use a dict for quick add/remove
        self.dependant_sprite_nodes = dict()
        #if sprites are deactivated, they will be moved to the inactive_dependants
        #move back to dependant_sprite_nodes when reactivated
        self.inactive_dependants = dict()

    ### DEPENDANT SPRITE FUNCTIONS ###

    #called by a node when it is deactivated
    def dependantSignalInactive(self, dependant_id):
        try:
            self.inactive_dependants[dependant_id] = self.dependant_sprite_nodes[dependant_id]
            del(self.dependant_sprite_nodes[dependant_id])
        except:
            pass

    #called by a node when it is activated
    def dependantSignalActive(self, dependant_id):
        try:
            self.dependant_sprite_nodes[dependant_id] = self.inactive_dependants[dependant_id]
            del (self.inactive_dependants[dependant_id])
        except:
            pass

    #called by a node when it is removed
    def dependantSignalRemoved(self, dependant_id):
        try:
            del (self.dependant_sprite_nodes[dependant_id])
        except:
            try:
                del (self.inactive_dependants[dependant_id])
            except:
                pass

    def signalRemovedToDependants(self):
        for node in self.dependant_sprite_nodes.values():
            node.removeEntityDependancy(self.entity_id)
        for node in self.inactive_dependants.values():
            node.removeEntityDependancy(self.entity_id)

    def getDependantIds(self):
        return self.dependant_sprite_nodes.keys()

    def addEntityDependancy(self, sprite_node):
        self.current_sprite_state.addEntityDependancy(self, sprite_node)

    def removeEntityDependancy(self, entity_id):
        self.current_sprite_state.removeEntityDependancy(self, entity_id)

    def clearEntityDependancies(self):
        self.current_sprite_state.clearEntityDependancies(self)

    ### CHECK FLAG STATE ###

    def dependantNetworkHasChanged(self):
        for dependant_sprite in self.dependant_sprite_nodes.values():
            if dependant_sprite.parentSpriteHasChanged():
                return True
        return False

    #Recursive call from the clones, this is the bottom; Clone wants to know if there is an update coming
    def parentSpriteNetworkHasChanged(self):
        if self.parentSpriteHasChanged():
            return True
        for dependant_sprite in self.dependant_sprite_nodes.values():
            if dependant_sprite.parentSpriteHasChanged():
                return True
        return False

    #Recursive call from the clones, this is the bottom; Clone wants to know if this sprite has changed
    def parentSpriteHasChanged(self):
        return self.current_sprite_state.parentSpriteHasChanged(self)

    #Recursive call from the clones, this is the bottom; Clone wants to know if state is AA
    def parentSpriteIsAlwaysActive(self):
        return self.current_sprite_state.isAlwaysActive()

    #returns true if sprite, or any clones or dependants are in an active cell
    def renderNetworkInActiveCell(self):
        if self.cellIsActive():
            return True
        if self.cloneNetworkInActiveCell():
            return True
        if self.dependantNetworkInActiveCell():
            return True
        return False

    def cloneNetworkInActiveCell(self):
        if self.horizontal_clone is not None:
            if self.horizontal_clone.cloneNetworkInActiveCell():
                return True
        if self.vertical_clone is not None:
            if self.vertical_clone.cloneNetworkInActiveCell():
                return True
        return False

    #Return true if any clones or dependants are in an active cell
    #Does not check if SELF is in an active cell (can use the cellIsActive() for this)
    def dependantNetworkInActiveCell(self):
        for sprite_node in self.dependant_sprite_nodes.values():
            if sprite_node.cellIsActive():
                return True
            if sprite_node.cloneNetworkInActiveCell():
                return True
        return False

    def isInOffscreenActives(self):
        return self.grid.isInOffscreenActives(self.entity_id)

    ### GRID MOVE FUNCTIONS ###
    #For the first time inserting a sprite into the grid
    def insertIntoGrid(self):
        self.current_sprite_state.insertIntoGrid(self)

    #Adds self and dependants to offscreen active IFF their cell is inactive
    #Used when changing to always active state, or cell changes from inactive to active
    def addNetworkToOffscreenActive(self):
        if not self.cellIsActive():
            self.grid.addToOffscreenActives(self)
        for sprite_node in self.dependant_sprite_nodes.values():
            if not sprite_node.cellIsActive():
                self.grid.addToOffscreenActives(sprite_node)

    #Just add dependants to offscreen actives, and notify that they are onscreen if you do
    def addDependantsToOffscreenActiveAndNotify(self):
        for entity_id, sprite_node in self.dependant_sprite_nodes.items():
            if not sprite_node.cellIsActive():
                self.grid.addToOffscreenActives(sprite_node)
                self.grid.notifySpriteOnscreen(entity_id)

    #If any of the dependant sprites are in offscreen actives, remove them
    #If a sprite is removed from offscreen actives, the EM is notified that the sprite is inactive
    def removeNetworkFromOffscreenActive(self):
        self.grid.removeFromOffscreenActives(self.entity_id)
        for sprite_node in self.dependant_sprite_nodes.values():
            self.grid.removeFromOffscreenActives(sprite_node.entity_id)

    #send the message for self and all dependants that the node is offscreen
    def notifyNetworkOffscreen(self):
        self.grid.notifySpriteOffscreen(self.entity_id)
        for sprite_node in self.dependant_sprite_nodes.values():
            self.grid.notifySpriteOffscreen(sprite_node.entity_id)

    # send the message for self and all dependants that the node is onscreen
    def notifyNetworkOnscreen(self):
        self.grid.notifySpriteOnscreen(self.entity_id)
        for sprite_node in self.dependant_sprite_nodes.values():
            self.grid.notifySpriteOnscreen(sprite_node.entity_id)

    ### SPRITE STATE FUNCTIONS ###

    def getSpriteStateEnum(self):
        return self.current_sprite_state.getSpriteStateEnum()
    def isActivated(self):
        return self.current_sprite_state.is_activated
    def isVisible(self):
        return self.current_sprite_state.is_visible
    def isEthereal(self):
        return self.current_sprite_state.is_ethereal
    def isAlwaysActive(self):
        return self.current_sprite_state.isAlwaysActive()
    #removes from grid, and offscreen actives.
    #Does not deal with the dependant sprites, only handles self
    def deactivateSprite(self):
        self.current_sprite_state = self.current_sprite_state.deactivateSprite(self)
    def removeNode(self):
        self.current_sprite_state = self.current_sprite_state.removeNode(self)
    def activateSprite(self):
        self.current_sprite_state = self.current_sprite_state.activateSprite(self)
    def setAlwaysActive(self):
        self.current_sprite_state = self.current_sprite_state.setAlwaysActive(self)
    def removeAlwaysActive(self):
        self.current_sprite_state = self.current_sprite_state.removeAlwaysActive(self)
    def setVisible(self):
        self.current_sprite_state = self.current_sprite_state.setVisible(self)
    def setInvisible(self):
        self.current_sprite_state = self.current_sprite_state.setInvisible(self)
    def setEthereal(self):
        self.current_sprite_state = self.current_sprite_state.setEthereal(self)
    def setTangible(self):
        self.current_sprite_state = self.current_sprite_state.setTangible(self)

    #called by an active cell
    def updateNodeActive(self):
        return self.current_sprite_state.updateNodeActive(self)

    def updateNodeOffscreenActive(self):
        return self.current_sprite_state.updateNodeOffscreenActive(self)

    ### CELL STATE FUNCTIONS ###
    def cellStateActiveToInactive(self):
        return self.current_sprite_state.cellStateActiveToInactive(self)

    def cellStateInactiveToActive(self):
        return self.current_sprite_state.cellStateInactiveToActive(self)

    ### SPRITE FRAME RENDER FUNCTIONS ###

    def _setPositionPtr(self):
        self.ground_position = self.particle.getPosition()
        self.updateWorldPosition()

    def updateWorldPosition(self):
        self.needs_sorting = True
        self.has_moved.value = False
        #Top left pixel to blit is the X coordinate from the ground, but add the height of the image and the Z offset to the Y component
        self.world_position = [self.ground_position[0],
                               self.ground_position[1] - self.ground_position[2] - self.image_coordinates[3] + 1]

    def resetRenderCoordinates(self):
        self.image_render_coordinates = list(self.image_coordinates)

    #updates the frame or image as needed, returns true if a change occurs
    #this is only called once per render.update() on the main sprite, and clears the dirty flags
    def updateSpriteFrame(self):
        #has some redundant actions here to take as few branches as possible on a given call
        if self.state_has_changed.value:
            self._updateBehaviorState() #also calls _updateAnimationFrame()
            self.image_render_coordinates = list(self.image_coordinates) #Create the copy because cropping may occur
            return True
        elif self.animation_has_flipped.value:
            self._updateAnimationFrame()
            self.image_render_coordinates = list(self.image_coordinates)
            return True
        return False #world position has not changed

    def _updateBehaviorState(self):
        self.behavior_state_id =self.behaviorFSM.getBehaviorState() #current behavior state
        #Sets the current list of image coordinates, which is indexed into by self._frame
        self.image_coordinates_list = self.state_image_coordinate_lists[self.behavior_state_id]
        self.image = self.state_images[self.behavior_state_id] #current sprite image sheet
        self._updateAnimationFrame()
        self.state_has_changed.value = False #clear the flag

    def _updateAnimationFrame(self):
        self.frame = self.behaviorFSM.frame #current frome
        self.image_coordinates = self.image_coordinates_list[self.frame] #The current portion of the current image
        self.animation_has_flipped.value = False #clear the flag

    #When the sprites state changes, call this to update clones states as needed
    def clonesVisibleToInvisible(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.changeVisibleToInvisible()
        if self.vertical_clone is not None:
            self.vertical_clone.changeVisibleToInvisible()

    #When the sprites state changes, call this to update clones states as needed
    def clonesInvisibleToVisible(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.changeInvisibleToVisible()
        if self.vertical_clone is not None:
            self.vertical_clone.changeInvisibleToVisible()

    def setClonesEthereal(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.setEthereal()
        if self.vertical_clone is not None:
            self.vertical_clone.setEthereal()

    def setClonesTangible(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.setTangible()
        if self.vertical_clone is not None:
            self.vertical_clone.setTangible()

    #Updated the RC of all clones
    def recursiveCloneUpdate(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.recursiveCloneUpdate()
        if self.vertical_clone is not None:
            self.vertical_clone.recursiveCloneUpdate()

    # self.image_render_coordinates - [X, Y, W, H]
    #clips the top/right side of the render_coordinates, and creates horizontal/vertical clones as needed
    def updateRenderBorders(self):
        #Clip the world position Y at 0 (do not render anything negative)
        if self.world_position[1] < 0:
            #adjust Y start of render coordinates, and the height
            self.image_render_coordinates[1] =self.image_coordinates[1] - self.world_position[1] #since negative this adds
            self.image_render_coordinates[3] =self.image_coordinates[3] + self.world_position[1] #since negative this subtracts
            self.world_position[1] = 0
        else:
            #reset image coordiantes to top left pixel
            self.image_render_coordinates[1] = self.image_coordinates[1]
            self.image_render_coordinates[3] = self.image_coordinates[3]

        #See if we cross the cell border to the right
        if self.world_position[0] + self.image_coordinates[2] - 1 > self.cell.borders[2]: #Right border
            #Adjust width of image to end at border of cell
            h_render_border = self.cell.borders[2] - self.world_position[0] + 1 #width
            #Check if world extends beyond right border of this cell
            if self.cell.borders[2] + 1 < self.grid.world_size[0]:
                #Create the new clone and setup it's coordinates
                if self.horizontal_clone is None:
                    self.horizontal_clone = HorizontalSpriteClone(self, self.isVisible(), self.isEthereal())
                    self.horizontal_clone.setWorldPosition([self.cell.borders[2]+1,
                                                            self.world_position[1]])
                    #If the horizonatal render coordinate goes over the next cell, the clone will create a clone
                    #Setting the coordinates sets a flag in the clone to check the render borders
                    self.horizontal_clone.setImageRenderCoordinates([self.image_coordinates[0] + h_render_border,
                                                                     self.image_render_coordinates[1],
                                                                     self.image_coordinates[2] - h_render_border,
                                                                     self.image_render_coordinates[3]])
                    self.horizontal_clone.setGrid(self.grid)
                    self.horizontal_clone.setLayer(self.layer)
                    self.grid.insertHorizontalClone(self.horizontal_clone)
                #X coordinate doesn't change, update Y/Z coordinate and render coordinates
                else:
                    self.horizontal_clone.world_position[1] = self.world_position[1]
                    self.horizontal_clone.setImageRenderCoordinates([self.image_coordinates[0] + h_render_border,
                                                                     self.image_render_coordinates[1],
                                                                     self.image_coordinates[2] - h_render_border,
                                                                     self.image_render_coordinates[3]])
                    #if the cell is inactive, then the clone will not be updated this loop
                    # If the clone has been moved, it needs to be updated!
                    if not self.horizontal_clone.cell.isActive():
                        self.horizontal_clone.updateRenderBorders()
            #only render the main sprite up to the border
            self.image_render_coordinates[2] = h_render_border
        #If not crossing border, may need to kill existing clone(s) to the right
        elif self.horizontal_clone is not None:
            self.horizontal_clone.killClones() #this clone is removed from the LL, as well as it's clones
            self.horizontal_clone = None
            self.image_render_coordinates[2] = self.image_coordinates[2] #Reset render width to entire image
        else:
            self.image_render_coordinates[2] = self.image_coordinates[2]  # Reset render width to entire image
        #See if crosses bottom border
        if self.world_position[1] + self.image_render_coordinates[3] - 1 > self.cell.borders[1]: #Bottom border
            #Adjust height of image to end at border of cell
            y_render_border = self.cell.borders[1] - self.world_position[1] + 1 #height
            # Check if world extends beyond bottom border of this cell
            if self.cell.borders[1] + 1 < self.grid.world_size[1]:
                if self.vertical_clone is None:
                    self.vertical_clone = VerticalSpriteClone(self, self.isVisible(), self.isEthereal())
                    self.vertical_clone.setWorldPosition([self.world_position[0],
                                                          self.cell.borders[1]+1])
                    self.vertical_clone.setImageRenderCoordinates([self.image_coordinates[0],
                                                                   self.image_render_coordinates[1] + y_render_border,
                                        #We pass the trimmed width here, because vertical clones don't trimm horizontally
                                                                   self.image_render_coordinates[2],
                                                                   self.image_render_coordinates[3] - y_render_border])
                    self.vertical_clone.setGrid(self.grid)
                    self.vertical_clone.setLayer(self.layer)
                    self.grid.insertVerticalClone(self.vertical_clone)
                else:
                    #just need to update X component, Y is always remains border of the cell
                    self.vertical_clone.world_position[0] = self.world_position[0]
                    self.vertical_clone.setImageRenderCoordinates([self.image_coordinates[0],
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
        return