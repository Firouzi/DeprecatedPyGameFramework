from enum import Enum

class CellStateEnum(Enum):
    CELL_STATE_DEFAULT = 0 #parent class, should not be used
    CELL_STATE_VISIBLE = 1 #Active AND Visible
    CELL_STATE_INACTIVE = 2
    CELL_STATE_INVISIBLE = 3 #Active, but Invisible

class SceneCell:
    def __init__(self, scene_layer, grid, master_cell):
        self.scene_layer = scene_layer
        self.grid = grid
        self.master_cell = master_cell

        #These are referenced often, so it is worth adding the extra pointer
        #note that each layer will have repeat cell_ids
        #however, if you go [scene id, layer_id, cell_id] you will get a unique combo for every cell
        self.cell_id = self.master_cell.cell_id
        self.borders =  self.master_cell.borders
        self.size = self.master_cell.size
        self.cell_state_enum = master_cell.cell_state_enum
        self.previous_cell_state_enum = master_cell.cell_state_enum

        #A Linked list for visible nodes which do include clones.  May be ethereal or tangible but need sorting either way
        self.head = None
        self.tail = None
        #These nodes need clones but no sorting, because they are not visible (#for invisible_tangible states)
        self.invisible_head = None
        self.invisible_tail = None

        #These nodes need no clones and no sorting, because there are not visible and do not interact with collisions
        self.invisible_ethereal_nodes = dict() #{entity_id : node}
        #add self as an observer to receive cell state changes
        self.master_cell.registerSceneCell(self)

    #Called by the master cell when the state changes
    def setCellState(self, cell_state_enum):
        self.cell_state_enum = cell_state_enum
