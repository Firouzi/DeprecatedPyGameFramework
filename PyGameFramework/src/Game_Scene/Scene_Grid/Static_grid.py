from Game_Scene.Scene_Cell.Static_cell import StaticCell
from Game_Scene.Scene_Grid.Scene_grid import SceneGrid

class StaticGrid(SceneGrid):
    def __init__(self, master_grid, scene_layer):
        super(StaticGrid, self).__init__(master_grid, scene_layer)

    def createCell(self, scene_layer, master_cell):
        return StaticCell(scene_layer, self, master_cell)
