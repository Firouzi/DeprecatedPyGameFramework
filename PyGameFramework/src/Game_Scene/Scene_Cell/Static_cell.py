from Scene_Cell.Scene_cell import SceneCell

#Static cells do not update, or call any change state methods
#Nodes are stored in a tuple, and only sorted once when all nodes are loaded
#Nodes can be added or removed and sorts can be called, but this is not generally efficient
#This cell is designed for scenery that doesn't change.
#Animated Tiles are allowed
#Static animated sprites are allowed but must remain the same size, as clones are only created on insert
class StaticCell(SceneCell):
    def __init__(self, scene_layer, grid, master_cell):
        super(StaticCell, self).__init__(scene_layer, grid, master_cell)