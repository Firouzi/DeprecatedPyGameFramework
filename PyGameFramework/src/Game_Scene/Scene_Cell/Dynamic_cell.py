from Game_Scene.Scene_Cell.Scene_cell import SceneCell, CellStateEnum

#Dynamic cells store nodes in linked lists, and are updated each render loop.
#They call change state methods on all nodes when they change state.  They are continually sorted
class DynamicCell(SceneCell):
    def __init__(self, scene_layer, grid, master_cell):
        super(DynamicCell, self).__init__(scene_layer, grid, master_cell)

    #Check the enum, because this is updated for all cells before stateChange occurs
    #For nodes that have dependants, they will see what the latest cell state is
    def isVisible(self):
        if self.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
            return True
        return False

    #Check the enum, because this is updated for all cells before stateChange occurs
    #For nodes that have dependants, they will see what the latest cell state is
    def isActive(self):
        if self.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
            return False
        return True

    #This can be a dict, because it is unsorted and we have no clones in it
    def insertInvisibleEtherealNode(self, node):
        node.cell = self
        self.invisible_ethereal_nodes[node.entity_id] = node

    def removeInvisibleEtherealNode(self, entity_id):
        try:
            del (self.invisible_ethereal_nodes[entity_id])
        except:
            pass

    def insertInvisibleTangibleNode(self, node):
        node.cell = self
        #self.invisible_tangible_nodes[node.entity_id] = node
        if self.invisible_head is None:
            self.invisible_head = node
            self.invisible_tail = node
            return
        temp = self.invisible_head
        self.invisible_head = node
        node.setNextNode(temp)
        temp.setPreviousNode(node)

    # The grid will use this method when a sprite should be added
    # The Cell decides if it should insert the sprite at the head or the tail based on y position
    def insertNode(self, node):
        # We do not check both, since we should never have a case where one is None and the other is not
        node.setCell(self)
        if self.head is None:
            self.head = node
            self.tail = node
            return
        #This is a rough guestimate of cell midpoints, but may make the sorting algorithm faster
        y_position = node.getGroundPosition()[1]
        # See if the y position is further from the top or bottom border to determine which end to insert on
        if y_position - self.borders[3] < self.borders[1] - y_position:
            self._insertHead(node)
        else:
            self._insertTail(node)

    #If we want to insert a node at the head regardless of ground position
    def insertAtHead(self, node):
        # We do not check both, since we should never have a case where one is None and the other is not
        node.setCell(self)
        if self.head is None:
            self.head = node
            self.tail = node
            return
        self._insertHead(node)

    #If we want to insert a node at the tail regardless of ground position
    def insertAtTail(self, node):
        # We do not check both, since we should never have a case where one is None and the other is not
        node.setCell(self)
        if self.head is None:
            self.head = node
            self.tail = node
            return
        self._insertTail(node)

    #we should never get here where the head or tail is None
    def _insertHead(self, node):
        #Put this node at the head, take the current head and make it the next node
        temp = self.head
        self.head = node
        node.setNextNode(temp)
        temp.setPreviousNode(node)

    #we should never get here where the head or tail is None
    def _insertTail(self, node):
        #Put this node at the tail, take the current tail and make it the prev node
        temp = self.tail
        self.tail = node
        temp.setNextNode(node)
        node.setPreviousNode(temp)

    #Checks to see if the passed in position is within cell bounds
    def residesInCell(self, world_position): #(int,int,int)
        if world_position[0] < self.borders[0] or \
            world_position[0] > self.borders[2] or \
            world_position[1] > self.borders[1] or \
            (world_position[1] < self.borders[3] != 0): #our Y position can be less than 0
            return False
        return True

    #Does the state change.  State to transition to is first set by enum in setCellState
    #This is done to allow all the pending state transitions to be set before any changes made
    #Entities will need to check the pending state of entities in other cells (Linked or Clones)
    def transitionCellState(self):
        if self.previous_cell_state_enum == self.cell_state_enum:
            return

        if self.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
            current_node = self.head
            while current_node is not None:
                next_node = current_node.next_node
                current_node.cellStateActiveToInactive()
                current_node = next_node
            #update the invisible linked list
            current_node = self.invisible_head
            while current_node is not None:
                next_node = current_node.next_node
                current_node.cellStateActiveToInactive()
                current_node = next_node
            for entity_id, node in self.invisible_ethereal_nodes.items():
                node.cellStateActiveToInactive()

        #Don't need to do a transition from Invisible <-> Active
        elif self.previous_cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
            current_node = self.head
            while current_node is not None:
                next_node = current_node.next_node
                current_node.cellStateInactiveToActive()
                current_node = next_node
            # update the invisible linked list
            current_node = self.invisible_head
            while current_node is not None:
                next_node = current_node.next_node
                current_node.cellStateInactiveToActive()
                current_node = next_node
            for entity_id, node in self.invisible_ethereal_nodes.items():
                node.cellStateInactiveToActive()
        #once we are done updating, we re-sync this variable.
        self.previous_cell_state_enum = self.cell_state_enum

    def update(self):
        #Verification Code
        if self.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
            print("Inactive Cell was updated id:" + str(self.cell_id))
            assert False
        #first update the visible linked list
        if self.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
            self._updateVisible()
        else:
            self._updateInvisible()
        #now update the invisible linked list
        current_node = self.invisible_head
        while current_node is not None:
            next_node = current_node.next_node
            current_node.updateNodeActive()
            current_node = next_node
        #Keep track of nodes that need to be removed from the invisible_ethereal_nodes list (they have moved to a new cell)
        #Nodes will be reinserted into other cells as needed, so simply remove them here
        remove_from_invisible_ethereals = list()
        for entity_id, node in self.invisible_ethereal_nodes.items():
            if node.updateNodeActive():
                remove_from_invisible_ethereals.append(entity_id)
        #remove any nodes from the offscreen_actives dict which have moved into active cells
        for entity_id in remove_from_invisible_ethereals:
            self.removeInvisibleEtherealNode(entity_id)

    #If the cell state is visible, use this update which also sorts
    def _updateVisible(self):
        current_node = self.head
        while current_node is not None:
            next_node = current_node.next_node
            # If returned true, need to do a sort
            if current_node.updateNodeActive():
                self.sortNode(current_node)
            current_node = next_node

    # If the cell state is invisible, use this update which doesn't sort
    def _updateInvisible(self):
        current_node = self.head
        while current_node is not None:
            next_node = current_node.next_node
            current_node.updateNodeActive()
            current_node = next_node

    def sortNode(self, node):
        #move backwards
        if node.previous_node is not None and node.ground_position[1] < node.previous_node.ground_position[1]:
            current_node_position = node
            prev_node_position = node.previous_node
            #pull the node out of the LL
            prev_node_position.next_node = node.next_node
            if node.next_node is not None:
                node.next_node.previous_node = prev_node_position
            else:
                self.setTail(prev_node_position)
            #search backwards for the correct spot to swap into
            while prev_node_position is not None and node.ground_position[1] < prev_node_position.ground_position[1]:
                current_node_position = prev_node_position
                prev_node_position = prev_node_position.previous_node
            #place node inbetween prev and current node positions
            if prev_node_position is None: #node is the new head
                self.setHead(node)
            else:
                prev_node_position.next_node = node
            node.previous_node = prev_node_position
            node.next_node = current_node_position
            current_node_position.previous_node = node
            node.needs_sorting = False
            return  # we don't want to sort move it forwards after moving it backwards!

        #move forwards
        if (node.next_node is not None and
                   (node.next_node.has_moved.value == True or
                    node.next_node.needs_sorting or
                    node.ground_position[1] > node.next_node.ground_position[1])):  # move forwards in the LL
            current_node_position = node
            next_node_position = node.next_node
            #pull the node out of the LL
            if node.previous_node is None:
                self.setHead(next_node_position)
            else:
                node.previous_node.next_node = next_node_position
            next_node_position.previous_node = node.previous_node
            #search forwards for the correct spot to swap into
            while (next_node_position is not None and
                       (next_node_position.has_moved.value == True or
                        next_node_position.needs_sorting or
                        node.ground_position[1] > next_node_position.ground_position[1])):  # move forwards in the LL
                current_node_position = next_node_position
                next_node_position = next_node_position.next_node
            #place node inbetween current and next node positions
            node.next_node = next_node_position
            if next_node_position is None:
                self.setTail(node)
            else:
                next_node_position.previous_node = node
            node.previous_node = current_node_position
            current_node_position.next_node = node
        node.needs_sorting = False
        return

    #if a node is removing itself and is the head (node has no previous)
    #then it will send the next cell (or none) to update the head pointer
    def setHead(self, node):
        self.head = node #could be None
    def setTail(self, node):
        self.tail = node #could be None
    def setInvisibleHead(self, node):
        self.invisible_head = node #could be None
    def setInvisibleTail(self, node):
        self.invisible_tail = node #could be None