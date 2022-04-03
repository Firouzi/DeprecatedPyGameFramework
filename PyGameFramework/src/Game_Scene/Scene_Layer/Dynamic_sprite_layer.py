from Game_Scene.Scene_Grid.Dynamic_grid import DynamicGrid
from Scene_layer import SceneLayer

class DynamicSpriteLayer(SceneLayer):
    def __init__(self, layer_id, scene, master_grid):
        super(DynamicSpriteLayer, self).__init__(layer_id, scene, master_grid)

    def createGrid(self):
        self.scene_grid = DynamicGrid(self.master_grid, self)

    def update(self):
        self.scene_grid.update()

    def insertNodeIntoGrid(self, entity_id, scene_node):
        scene_node.setGrid(self.scene_grid)
        scene_node.setLayer(self)
        scene_node.insertIntoGrid()
