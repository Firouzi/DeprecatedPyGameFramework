class SceneLayer:
    def __init__(self, layer_id, scene, master_grid):
        self.layer_id = layer_id
        self.scene = scene
        self.master_grid = master_grid
        self.scene_grid = None
        self.layer_type = 1
        self.is_active = False
        #Note - layers must always be active, to keep their cell states syced with master grid
        #So there is no 'is active' attribute.  However, there could be an 'is visible' attribute added

        self.createGrid()

    def isActive(self):
        return self.is_active

    def activateLayer(self):
        self.is_active = True

    def deactivateLayer(self):
        self.is_active = False

    #overridden in child classes to create the correct grid type
    def createGrid(self):
        print("SceneLayer.createGrid base called")
        assert False

    def update(self):
        print("update called in SceneLayer base class")
        assert False

    def insertNodeIntoGrid(self, entity_id, scene_node):
        print("insertNodeIntoGrid called in SceneLayer base class")
        assert False

    def removeSceneGrid(self):
        self.master_grid.removeSceneGrid(self.layer_id)