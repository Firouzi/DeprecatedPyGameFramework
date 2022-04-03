from Game_Scene.Scene_Cell.Scene_cell import CellStateEnum

### Common functions used in multiple suites ###

#returns True Iff sprite or clone or dependant in an active cell, else False
def _spriteNetworkInActiveCellTest_(sprite_node):
    if sprite_node.cell is None:
        return False
    if _isActiveCell_(sprite_node.cell):
        return True
    if _cloneInActiveCell_(sprite_node):
        return True
    for dependant_node in sprite_node.dependant_sprite_nodes.values():
        if _isActiveCell_(dependant_node.cell):
            return True
        if _cloneInActiveCell_(dependant_node):
            return True
    return False

#returns true IFF any of the clones of the sprite node are in an active cell
def _cloneInActiveCell_(sprite_node):
    h_clone = sprite_node.horizontal_clone
    while h_clone is not None:
        if _isActiveCell_(h_clone.cell):
            return True
        v_clone = h_clone.vertical_clone
        while v_clone is not None:
            if _isActiveCell_(v_clone.cell):
                return True
            v_clone = v_clone.vertical_clone
        h_clone = h_clone.horizontal_clone
    v_clone = sprite_node.vertical_clone
    while v_clone is not None:
        if _isActiveCell_(v_clone.cell):
            return True
        v_clone = v_clone.vertical_clone

def _isActiveCell_(cell):
    if cell.cell_state_enum == CellStateEnum.CELL_STATE_INVISIBLE or \
            cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
        return True
    return False

#returns true if node is derived from SpriteClone
def _isCloneBased_(node):
    node_class = node.__class__
    node_bases = node_class.__bases__
    for node_base in node_bases:
        if __isSpriteClone__(node_base):
            return True
    return False

#returns true if node is derived from HorizontalSpriteClone
def _isHorizontalCloneBased_(node):
    node_class = node.__class__
    if node_class.__name__ == "HorizontalSpriteClone":
        return True
    node_bases = node_class.__bases__
    for node_base in node_bases:
        if __isHorizontalSpriteClone__(node_base):
            return True
    return False

#returns true if node is derived from VerticalSpriteClone
def _isVerticalCloneBased_(node):
    node_class = node.__class__
    if node_class.__name__ == "VerticalSpriteClone":
        return True
    node_bases = node_class.__bases__
    for node_base in node_bases:
        if __isVerticalSpriteClone__(node_base):
            return True
    return False

#returns a node from a cell based on its entity_id
#returns False if multiple entries found with the same entity_id
#returns None if not found
def _getNodeByEntityIdInCell_(entity_id, cell, invisible = False):
    if invisible:
        if cell.invisible_head is None:
            return None
    else:
        if cell.head is None:
            return None
    retVal = None
    if invisible:
        current =  cell.invisible_head
    else:
        current = cell.head
    while current is not None:
        if current.entity_id == entity_id:
            if retVal is None:
                retVal = current
            else:
                print("test_scene_functions - found duplicate entity in cell, id: "+ str(entity_id))
                return False
        current = current.next_node
    return retVal

#return the ceiling of 'a divided by b'
def _ceiling_(a,b):
    return -(-a//b)

### Helper Functions ###
    #only call these internally here

#recursive call that goes up the class chain until either SpriteClone is found (return True)
#or "object" is found (return false)
def __isSpriteClone__(base_class):
    if base_class.__name__ == "object":
        return False
    if base_class.__name__ == "SpriteClone":
        return True
    base_base_classes = base_class.__bases__
    for base_base_class in base_base_classes:
        if __isSpriteClone__(base_base_class):
            return True
    #if we get here than we checked all possible branches and there is no SpriteClone found
    return False

#recursive call that goes up the class chain until either SpriteClone is found (return True)
#or "object" is found (return false)
def __isHorizontalSpriteClone__(base_class):
    if base_class.__name__ == "object":
        return False
    if base_class.__name__ == "HorizontalSpriteClone":
        return True
    base_base_classes = base_class.__bases__
    for base_base_class in base_base_classes:
        if __isHorizontalSpriteClone__(base_base_class):
            return True
    #if we get here than we checked all possible branches and there is no SpriteClone found
    return False

#recursive call that goes up the class chain until either SpriteClone is found (return True)
#or "object" is found (return false)
def __isVerticalSpriteClone__(base_class):
    if base_class.__name__ == "object":
        return False
    if base_class.__name__ == "VerticalSpriteClone":
        return True
    base_base_classes = base_class.__bases__
    for base_base_class in base_base_classes:
        if __isVerticalSpriteClone__(base_base_class):
            return True
    #if we get here than we checked all possible branches and there is no SpriteClone found
    return False