from Game_Scene.Test.Mock_Classes.Grid_utility_mock import MockFlag

#A node in a linked list, which is contained within a Scene_Cell
class SceneNode:
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.previous_node = None
        self.next_node = None
        self.cell = None #ptr to the cell which contains this SceneNode
        self.grid = None #ptr to grid which contains the cell
        self.layer = None #ptr to scene layer which contains the grid
        #Clones are reference to the same entity as this node, but in a different cell
        #hclones can also contain hclones and vclones, vclones can also contain vclones
        self.horizontal_clone = None
        self.vertical_clone = None

        self.ground_position = [0,0,0] #X,Y,Z position of the particle, bottom left corner of sprite
        self.world_position =[0,0] #top left pixel of sprite on the world map, we add Z component to the Y
        self.has_moved = MockFlag(False)
        self.needs_sorting = True

    def getEntityId(self):
        return self.entity_id

    #When sorting within a cell, we want to use the ground position
    #For the main sprite, this will be the same as it's world position
    #For subsprites and clones, the ground position =/= the world position
    def getGroundPosition(self):
        return self.ground_position

    #This is not relative to it's groundpositin or sorting order, it is relative to the world map
    #A sprite which is above the ground, can be rendered in a different cell from the one of it's ground position
    def getWorldPosition(self):
        return self.world_position

    #Overridden in sprite, checking the sprite state
    def isActivated(self):
        print("isActivated called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    def isAlwaysActive(self):
        print("isAlwaysActive called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    def cellIsActive(self):
        if self.cell is not None:
            return self.cell.isActive()
        return False

    def cellIsVisible(self):
        if self.cell is not None:
            return self.cell.isVisible()
        return False

    def getPreviousNode(self):
        return self.previous_node

    def getNextNode(self):
        return self.next_node

    def setPreviousNode(self, node): #can be None
        self.previous_node = node

    def setNextNode(self, node): #can be None
        self.next_node = node

    def setCell(self, cell):
        self.cell = cell

    def setGrid(self, grid):
        self.grid = grid

    def setLayer(self, layer):
        self.layer = layer

    #Updates the prev and next pointers of the connected nodes, as well as the head/tail of the cell
    #These updates can be setting prev/next and tail/head to None if applicable
    def removeSelfFromLinkedList(self):
        if self.previous_node is None:  #This node is the head
            self.cell.setHead(self.next_node)
        else:
            self.previous_node.setNextNode(self.next_node)
        if self.next_node is None: #This node is the tail
            self.cell.setTail(self.previous_node)
        else:
            self.next_node.setPreviousNode(self.previous_node)
        self.next_node = None
        self.previous_node = None

    def removeSelfFromInvisibleLList(self):
        if self.previous_node is None:  #This node is the head
            self.cell.setInvisibleHead(self.next_node)
        else:
            self.previous_node.setNextNode(self.next_node)
        if self.next_node is None: #This node is the tail
            self.cell.setInvisibleTail(self.previous_node)
        else:
            self.next_node.setPreviousNode(self.previous_node)
        self.next_node = None
        self.previous_node = None

    def setCloneMoveFlags(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.setCloneMoveFlags()
        if self.vertical_clone is not None:
            self.vertical_clone.setCloneMoveFlags()

    def killClones(self):
        if self.horizontal_clone is not None:
            self.horizontal_clone.killClones()
            self.horizontal_clone = None
        if self.vertical_clone is not None:
            self.vertical_clone.killClones()
            self.vertical_clone = None

    def removeNode(self):
        print("removeNode called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Returns true iff any clones (recursively) are in a cell which is active
    def cloneNetworkInActiveCell(self):
        print("cloneNetworkInActiveCell called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Returns true iff any dependants are in an active cell (child class defines what a dependant is)
    def dependantNetworkInActiveCell(self):
        print("dependantNetworkInActiveCell called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Returns true is a dirty flag is set in any dependants
    def dependantNetworkHasChanged(self):
        print("dependantNetworkHasChanged called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Adds self and any dependants to offscreen actives list in the grid
    def addNetworkToOffscreenActive(self):
        print("addNetworkToOffscreenActive called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Removes self and any dependants to offscreen actives list in the grid
    def removeNetworkFromOffscreenActive(self):
        print("removeNetworkFromOffscreenActive called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Call the grid notify offscreen method for self and all dependants
    def notifyNetworkOffscreen(self):
        print("notifyNetworkOffscreen called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    # Call the grid notify onscreen method for self and all dependants
    def notifyNetworkOnscreen(self):
        print("notifyNetworkOnscreen called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #forces an update on all clones recursively
    def recursiveCloneUpdate(self):
        print("recursiveCloneUpdate called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #call this to insert the node into the grid (should have a ref to the grid already)
    def insertIntoGrid(self):
        print("insertIntoGrid called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #called by an active cell during scene update
    def updateNodeActive(self):
        print("updateNodeActive called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Called by grid if node is in offscreen actives list
    #Returns an empty list if the node should remain as offscreen active
    #Return a list of entity ids that should be removed from offscreen actives
    def updateNodeOffscreenActive(self):
        print("updateNodeOffscreenActive called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Called by a cell which is changing state from active to inactive
    def cellStateActiveToInactive(self):
        print("cellStateActiveToInactive called in SceneNode base class, id: " + str(self.entity_id))
        assert False

    #Called by a cell which is changing state from inactive to active
    def cellStateInactiveToActive(self):
        print("cellStateInactiveToActive called in SceneNode base class, id: " + str(self.entity_id))
        assert False