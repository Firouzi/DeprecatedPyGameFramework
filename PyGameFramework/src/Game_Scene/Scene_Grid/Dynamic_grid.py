from Game_Scene.Scene_Cell.Dynamic_cell import DynamicCell
from Game_Scene.Scene_Cell.Scene_cell import CellStateEnum
from Game_Scene.Scene_Grid.Scene_grid import SceneGrid

class DynamicGrid(SceneGrid):
    def __init__(self, master_grid, scene_layer):
        super(DynamicGrid, self).__init__(master_grid, scene_layer)
        #We initialize the value to -1, that way if change states cause a sprite insert, or clone
            #The insert is always treated as inser 'forward' (since no cells updated as yet)
        self.current_update_cell_id = -1

        #{entity_id : node}
        self.offscreen_active_nodes = dict()
        #we don't need to store these in a cell, and do not need to do any render updates to them
        self.always_active_invisible_ethereal_nodes = dict()

    def createCell(self, scene_layer, master_cell):
        return DynamicCell(scene_layer, self, master_cell)

    #needed for sprite state changes, not normal flow
    def notifySpriteOnscreen(self, entity_id):
        self.notify_sprite_onscreen(entity_id)

    #needed for sprite state changes, not normal flow
    def notifySpriteOffscreen(self, entity_id):
        self.notify_sprite_offscreen(entity_id)

    def addToAlwaysActiveInvisibleEthereals(self, node):
        try:
            #if the node is part of offscreen actives, remove it
            del (self.offscreen_active_nodes[node.entity_id])
        except:
            pass
        self.always_active_invisible_ethereal_nodes[node.entity_id] = node

    def removeFromAlwaysActiveInvisibleEthereals(self, entity_id):
        try:
            del (self.always_active_invisible_ethereal_nodes[entity_id])
        except:
            pass

    def isInOffscreenActives(self, entity_id):
        if self.offscreen_active_nodes.get(entity_id) is None:
            return False
        return True

    def addToOffscreenActives(self, node):
        self.offscreen_active_nodes[node.entity_id] = node

    #If the entity is part of the offScreen Actives, remove it from that list
    #Returns true if succesfull, indicate the entity WAS in offscreen actives
    def removeFromOffscreenActives(self, entity_id):
        try:
            del (self.offscreen_active_nodes[entity_id])
            return True
        except:
            return False

    def update(self):
        # Offscreen Active node updates
        remove_from_offscreen = list()
        for entity_id, node in self.offscreen_active_nodes.items():
            # updateNodeOffscreenActive returns id's to return if the node has moved into an active cell
            #or if the network is no longer in an active cell at all
            remove_from_offscreen += node.updateNodeOffscreenActive()
        # remove any nodes from the offscreen_actives dict which have moved into active cells
        for remove_id in remove_from_offscreen:
            try:
                del (self.offscreen_active_nodes[remove_id])
            except:
                pass
        #self.update_cell_ranges = dict()  # {row : [[col_min1, colmax1], [col_min2, col_max2],...]}
        #self.row_update_keys = list()  # list of row ints in ascending order
        update_cell_ranges =  self.master_grid.update_cell_ranges
        for row_index in self.master_grid.row_update_keys:
            active_row = update_cell_ranges[row_index]
            for col_range in active_row:
                self.current_update_cell_id = (row_index*self.numb_cols) + col_range[0]
                for col_index in range(col_range[0], col_range[1] + 1):
                    self._scene_cells[row_index][col_index].update()
                    self.current_update_cell_id += 1
        self.current_update_cell_id = -1

    #For active, and ethereal nodes
    def insertActiveNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertNode(node)
        # if a visible node is inserted into an inactive cell, update the RB
        # If the update RB creates clones in an active cell, send the node to offscreen actives
        if not cell.isActive():
            node.updateRenderBorders()
            if node.parentSpriteHasChanged() or node.renderNetworkInActiveCell():
                self.addToOffscreenActives(node)
            # Note, since new nodes always have flags set until first updated,
            # we don't hit this branch - which is OK, they will be handled on the next update in offscreen actives
            else:
                self.notify_sprite_offscreen(node.entity_id)

    #invisible tangible nodes create clones, but do not need to be in a sorted list
    def insertInvisibleTangibleNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertInvisibleTangibleNode(node)
        # if a visible node is inserted into an inactive cell, update the RB
        # If the update RB creates clones in an active cell, send the node to offscreen actives
        if not cell.isActive():
            node.updateRenderBorders()
            if node.parentSpriteHasChanged() or node.renderNetworkInActiveCell():
                self.addToOffscreenActives(node)
            # Note, since new nodes always have flags set until first updated,
            # we don't hit this branch - which is OK, they will be handled on the next update in offscreen actives
            else:
                self.notify_sprite_offscreen(node.entity_id)

    def insertInvisibleEtherealNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        if cell_row < 0:  # world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertInvisibleEtherealNode(node)
        if not cell.isActive():
            self.notify_sprite_offscreen(node.entity_id)

    def insertAlwaysActiveNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertNode(node)
        # if a visible node is inserted into an inactive cell, update the RB
        # If the update RB creates clones in an active cell, send the node to offscreen actives
        if not cell.isActive():
            self.addToOffscreenActives(node)

    def insertAlwaysActiveInvisibleTangibleNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertInvisibleTangibleNode(node)
        # if a visible node is inserted into an inactive cell, update the RB
        # If the update RB creates clones in an active cell, send the node to offscreen actives
        if not cell.isActive():
            self.addToOffscreenActives(node)

    #For nodes that have already been in the grid, but removed from cells due to a state change
    #This only handles replacing the node in the cell, does not update the node
    def reinsertNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertNode(node)

    def reinsertInvisibleTangibleNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertInvisibleTangibleNode(node)

    def reinsertInvisibleEtherealNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        # The Ground position is restricted to 0,0 and the borders of the world map
        # The World position Y value is offset due to the image size and Z offset (we want top left corner of image)
        # If we are over the top of the map, we need to stay in the top row
        if cell_row < 0:
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertInvisibleEtherealNode(node)

    #called by active nodes when moving to a new cell
    def moveActiveNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1]//self.cell_size[1]
        cell_col = position[0]//self.cell_size[0]
        if cell_row < 0: #world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell_id = cell.cell_id
        cell.insertNode(node)
        #Moving backwards to already updated cell
        if cell_id < self.current_update_cell_id:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                #there is a possibility of the sprite image crossing from inactive to an active cell
                #if this occurs, then we need to move this node to offscreen inactives and continue updating it
                node.updateRenderBorders()
                #if any clones have spawned forward into an active cell due to updateRenderBorders(), this will be true
                #also true if sprite has a dependant sprite in an active node
                if node.renderNetworkInActiveCell():
                    self.addToOffscreenActives(node)
                #if this cell moves to inactive cell, and no other dependants in active cell
                #remove them all from offscreen Actives, notify EM that this network is offscreen
                else:
                    node.removeNetworkFromOffscreenActive()
                    self.notify_sprite_offscreen(node.entity_id)
                    for entity_id in node.dependant_sprite_nodes.keys():
                        self.notify_sprite_offscreen(entity_id)
            elif cell.cell_state_enum == CellStateEnum.CELL_STATE_INVISIBLE:
                node.updateRenderBorders()
            else:
                node.updateRenderBorders()
                cell.sortNode(node)
        #Moving Forwards to cell not updated as yet
        else:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
                if node.renderNetworkInActiveCell():
                    node.addNetworkToOffscreenActive()
                #if this cell moves to inactive cell, and no other dependants in active cell
                #remove them all from offscreen Actives, notify EM that this network is offscreen
                else:
                    node.removeNetworkFromOffscreenActive()
                    self.notify_sprite_offscreen(node.entity_id)
                    for entity_id in node.dependant_sprite_nodes.keys():
                        self.notify_sprite_offscreen(entity_id)
            else:
                node.has_moved.value = True #Force an update when we get to this cell/node

    def moveInvisibleTangibleNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        if cell_row < 0:  # world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell_id = cell.cell_id
        cell.insertInvisibleTangibleNode(node)
        # Moving backwards to already updated cell
        if cell_id < self.current_update_cell_id:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                # there is a possibility of the sprite image crossing from inactive to an active cell
                # if this occurs, then we need to move this node to offscreen inactives and continue updating it
                node.updateRenderBorders()
                # if any clones have spawned forward into an active cell due to updateRenderBorders(), this will be true
                # also true if sprite has a dependant sprite in an active node
                if node.renderNetworkInActiveCell():
                    self.addToOffscreenActives(node)
                # if this cell moves to inactive cell, and no other dependants in active cell
                # remove them all from offscreen Actives, notify EM that this network is offscreen
                else:
                    node.removeNetworkFromOffscreenActive()
                    self.notify_sprite_offscreen(node.entity_id)
                    for entity_id in node.dependant_sprite_nodes.keys():
                        self.notify_sprite_offscreen(entity_id)
            else:
                node.updateRenderBorders()
        # Moving Forwards to cell not updated as yet
        else:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
                if node.renderNetworkInActiveCell():
                    node.addNetworkToOffscreenActive()
                # if this cell moves to inactive cell, and no other dependants in active cell
                # remove them all from offscreen Actives, notify EM that this network is offscreen
                else:
                    node.removeNetworkFromOffscreenActive()
                    self.notify_sprite_offscreen(node.entity_id)
                    for entity_id in node.dependant_sprite_nodes.keys():
                        self.notify_sprite_offscreen(entity_id)
            else:
                node.has_moved.value = True  # Force an update when we get to this cell/node

    # called by active invisible ethereal nodes when moving to a new cell
    def moveInvisibleEtherealNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1]//self.cell_size[1]
        cell_col = position[0]//self.cell_size[0]
        if cell_row < 0: #world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell.insertInvisibleEtherealNode(node)
        if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
            if node.dependantNetworkInActiveCell():
                self.addToOffscreenActives(node)
            #if this cell moves to inactive cell, and no other dependants in active cell
            #remove them all from offscreen Actives, notify EM that this network is offscreen
            else:
                node.removeNetworkFromOffscreenActive()
                self.notify_sprite_offscreen(node.entity_id)
                for entity_id in node.dependant_sprite_nodes.keys():
                    self.notify_sprite_offscreen(entity_id)

    #Called by always_active node when when moving to a new cell
    def moveAlwaysActiveNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1]//self.cell_size[1]
        cell_col = position[0]//self.cell_size[0]
        if cell_row < 0: #world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell_id = cell.cell_id
        cell.insertNode(node)
        #Moving backwards to already updated cell
        if cell_id < self.current_update_cell_id:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
                self.addToOffscreenActives(node)
            elif cell.cell_state_enum == CellStateEnum.CELL_STATE_INVISIBLE:
                node.updateRenderBorders()
            else:
                node.updateRenderBorders()
                cell.sortNode(node)
        #Moving Forwards to cell not updated as yet
        else:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
                self.addToOffscreenActives(node)
            else:
                node.has_moved.value = True  # Force an update when we get to this cell/node

    # Called by always_active node when when moving to a new cell
    def moveAlwaysActiveInvisibleNode(self, node):
        position = node.getWorldPosition()
        cell_row = position[1] // self.cell_size[1]
        cell_col = position[0] // self.cell_size[0]
        if cell_row < 0:  # world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell_id = cell.cell_id
        cell.insertInvisibleTangibleNode(node)
        # Moving backwards to already updated cell
        if cell_id < self.current_update_cell_id:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
                self.addToOffscreenActives(node)
            else:
                node.updateRenderBorders()
        # Moving Forwards to cell not updated as yet
        else:
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
                self.addToOffscreenActives(node)
            else:
                node.has_moved.value = True  # Force an update when we get to this cell/node

    def insertHorizontalClone(self, node):
        position = node.getWorldPosition()
        cell_row = position[1]//self.cell_size[1]
        cell_col = position[0]//self.cell_size[0]
        if cell_row < 0: #world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell_id = cell.cell_id
        #Moving backwards to already updated cell
        if cell_id < self.current_update_cell_id:
            if node.isVisible():
                cell.insertNode(node)
                node.updateRenderBorders()
                if cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
                    cell.sortNode(node)
            else:
                cell.insertInvisibleTangibleNode(node)
                node.updateRenderBorders()
        #clone being into a currenlty updating cell
        #IE A Sprite in this cell has moved back a cell, and passed a clone forward into this cell
        elif cell_id == self.current_update_cell_id:
            # We insert at the front of the LL to ensure we sort it into position
            #actions depend on the type of cell being inserted into
            #Since the update id is the current cell, we know that cell is active
            if node.isVisible():
                cell.insertAtHead(node)
                node.updateRenderBorders()
                if cell.cell_state_enum != CellStateEnum.CELL_STATE_INVISIBLE:
                    cell.sortNode(node)
            else:
                cell.insertInvisibleTangibleNode(node)
                node.updateRenderBorders()
        #Moving Forwards to cell not updated as yet
        else:
            if node.isVisible():
                cell.insertNode(node)
            else:
                cell.insertInvisibleTangibleNode(node)
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()

    def insertVerticalClone(self, node):
        position = node.getWorldPosition()
        cell_row = position[1]//self.cell_size[1]
        cell_col = position[0]//self.cell_size[0]
        if cell_row < 0: #world position can be negative on the Y axis because of image offset
            cell_row = 0
        cell = self._scene_cells[cell_row][cell_col]
        cell_id = cell.cell_id
        #Moving backwards to already updated cell
        if cell_id < self.current_update_cell_id:
            if node.isVisible():
                cell.insertNode(node)
                node.updateRenderBorders()
                if cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
                    cell.sortNode(node)
            else:
                cell.insertInvisibleTangibleNode(node)
                node.updateRenderBorders()
        #clone being into a currenlty updating cell
        #IE A Sprite in this cell has moved back a cell, and passed a clone forward into this sell
        elif cell_id == self.current_update_cell_id:
            #We insert at the front of the LL to ensure we sort it into position
            #actions depend on the type of cell being inserted into
            if node.isVisible():
                cell.insertAtHead(node)
                node.updateRenderBorders()
                if cell.cell_state_enum != CellStateEnum.CELL_STATE_INVISIBLE:
                    cell.sortNode(node)
            else:
                cell.insertInvisibleTangibleNode(node)
                node.updateRenderBorders()
        #Moving Forwards to cell not updated as yet
        else:
            if node.isVisible():
                cell.insertNode(node)
            else:
                cell.insertInvisibleTangibleNode(node)
            if cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                node.updateRenderBorders()
