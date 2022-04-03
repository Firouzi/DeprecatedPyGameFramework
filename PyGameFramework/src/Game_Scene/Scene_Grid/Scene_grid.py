class SceneGrid:
    def __init__(self, master_grid, scene_layer):
        self.master_grid = master_grid
        self.scene_layer = scene_layer  #parent

        self.notify_sprite_offscreen = master_grid.notify_sprite_offscreen
        self.notify_sprite_onscreen = master_grid.notify_sprite_onscreen
        self.world_size = master_grid.world_size
        self.cell_size = master_grid.cell_size
        self.numb_rows = master_grid.numb_rows
        self.numb_cols = master_grid.numb_cols
        self._scene_cells = list()
        self.createGrid()

    def createGrid(self):
        for row in range(0, self.numb_rows):
            cell_row = list()
            for col in range(0, self.numb_cols):
                master_cell = self.master_grid.master_cells[row][col]
                scene_cell = self.createCell(self.scene_layer, master_cell)
                scene_cell.setCellState(master_cell.getCellStateEnum())
                cell_row.append(scene_cell)
            self._scene_cells.append(cell_row)

    #Over-ride in child classes to create correct cell type
    def createCell(self, scene_layer, master_cell):
        print("SceneGrid.createCell base called")
        assert False

    def transitionCells(self, row_range, col_range):
        for row in range(row_range[0], row_range[1]):
            for col in range(col_range[0], col_range[1]):
                self._scene_cells[row][col].transitionCellState()

