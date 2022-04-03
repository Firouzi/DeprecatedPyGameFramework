
#A Master grid has an array of master cells, which the cell instances each reference
#most of the data is the same across every layer, so no need to save it acorss each isntance
class MasterCell:
    def __init__(self, master_grid, cell_id, borders, row, col, cell_state_enum):
        self.master_grid = master_grid
        self.id = cell_id
        self.cell_id = self.id
        #temp lables, convenient reference during debugging
        self.borders_labels_temp = ("LEFT", "BOTTOM", "RIGHT", "TOP")
        self.borders = borders  # [left, bottom, right, top] - inclusive of pixel
        self.size = (borders[2] - borders[0] + 1, borders[1] - borders[3] + 1)
        self.row = row
        self.col = col
        self.cell_state_enum = cell_state_enum

        #When the master cell transitions, it sets the cell state on all of its scene cells
        self.scene_cells = list()

    def getCellStateEnum(self):
        return self.cell_state_enum

    #The master cell gets it's cell set by the master grid, then sets the states of all registered cells
    #There will be a registered cell for every layer (every layer that has a grid)
    def registerSceneCell(self, scene_cell):
        self.scene_cells.append(scene_cell)

    def setCellState(self, cell_state_enum):
        self.cell_state_enum = cell_state_enum
        for scene_cell in self.scene_cells:
            scene_cell.setCellState(cell_state_enum)