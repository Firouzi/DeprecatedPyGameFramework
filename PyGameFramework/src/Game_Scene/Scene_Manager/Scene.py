from Game_Scene.Scene_Grid.Master_grid import SceneMasterGrid
from Dynamic_sprite_layer import DynamicSpriteLayer

SCENE_LAYER_DYNAMIC_SPRITE = 1

class Scene:
    def __init__(self,
                 scene_id, #int
                 world_size, #[int, int]px
                 cell_size, #[int, int]px
                 tile_size): #[int, int]px
        self.scene_id = scene_id
        self.world_size = world_size
        self.cell_size = cell_size
        self.tile_size = tile_size
        self._cameras = dict() #{camera_id : Camera}
        self._scene_master_grid = SceneMasterGrid(self)
        self._scene_layers = dict()
        self.is_active = False
        #Map from entity id to layer
        self._entity_id_by_layer = dict() #{entity_id : layer_id}

        #All sprites, active or inactive are stored in _sprites[]
        #There is not iteration of this list (iteration happens in the grid),
        #so there is no need for an inactives list
        self._sprites = dict() #{(int)entity_id : SpriteMock}

    def activateScene(self):
        if self.is_active:
            print("Attempted to activate already active scene: ", self.scene_id)
            assert False
        self.is_active = True
        self._scene_master_grid.activateGrid()

    def deactivateScene(self):
        if not self.is_active:
            print("Attempted to deactivate already inactive scene: ", self.scene_id)
            assert False
        self.is_active = False
        #Only needed if an already active scene is deactivated
        self._scene_master_grid.deactivateGrid()

    def getEntityIds(self):
        return list(self._sprites.keys())

    def attachCamera(self, camera_id, camera, position):
        self._cameras[camera_id] = camera
        camera.attachToScene(self, position)
        self._scene_master_grid.attachCamera(camera_id, camera)

    def detachCamera(self, camera_id):
        try:
            del(self._cameras[camera_id])
        except:
            pass

    #Set the funtion pointers for the grid to the entity manager for this scene
    def setMasterGridNotify(self, notify_onscreen, notify_offscreen):
        self._scene_master_grid.notify_sprite_onscreen = notify_onscreen
        self._scene_master_grid.notify_sprite_offscreen = notify_offscreen

    def createSceneLayer(self, layer_id, layer_type):
        new_scene_layer = None
        if layer_type == SCENE_LAYER_DYNAMIC_SPRITE:
            new_scene_layer = DynamicSpriteLayer(layer_id, self, self._scene_master_grid)
            self.addSceneLayer(layer_id, new_scene_layer)
        self._scene_master_grid.addSceneGrid(layer_id, new_scene_layer.scene_grid)

    def addSceneLayer(self, layer_id, scene_layer):
        self._scene_layers[layer_id] = scene_layer

    def getEntityIdsFromLayer(self, layer_id):
        try:
            entity_ids_in_layer = list()
            for entity_id, entity_layer_id in self._entity_id_by_layer.items():
                if entity_layer_id == layer_id:
                    entity_ids_in_layer.append(entity_id)
            return entity_ids_in_layer
        except:
            print("Exception caught in getEntityIdsFromLayer, ",layer_id)
            assert False

    #Note, this doesn't have to be extremely effecient as it is a weird operation to call, removing a layer
        #Not Can also simply deactivate a layer
    def removeSceneLayer(self, layer_id):
        try:
            self._scene_layers[layer_id].removeSceneGrid()
            del(self._scene_layers[layer_id])
        except:
            print("Exception caught in removeSceneLayer, ", layer_id)
            assert False

    #Add dependants AFTER inserting sprite
    def addNode(self, layer_id, entity_id, scene_node):
        self._sprites[entity_id] = scene_node
        self._scene_layers[layer_id].insertNodeIntoGrid(entity_id, scene_node)
        if self._entity_id_by_layer.get(entity_id) is not None:
            print("Duplicate entity id in layer")
            assert False
        self._entity_id_by_layer[entity_id] = layer_id

    def removeNode(self, entity_id):
        self._sprites[entity_id].removeNode() #pulls it out of the cell/grid
        del(self._sprites[entity_id])
        del(self._entity_id_by_layer[entity_id])

    #When an entity is removed as a dependant, all of it's dependants are cleared
    #This is essentially removing an entity from a dependant network completely
    def clearEntityDependancies(self, entity_id):
        self._sprites[entity_id].clearEntityDependancies()

    def removeEntityDependancy(self, entity_id, dependant_entity_id):
        self._sprites[entity_id].removeEntityDependancy(dependant_entity_id)

    def addEntityDependancy(self, entity_id, dependant_entity_id):
        self._sprites[entity_id].addEntityDependancy(self._sprites[dependant_entity_id])

    def activateEntity(self, entity_id):
        self._sprites[entity_id].activateSprite()

    def deactivateEntity(self, entity_id):
        self._sprites[entity_id].deactivateSprite()

    def setAlwaysActive(self, entity_id):
        self._sprites[entity_id].setAlwaysActive()

    def removeAlwaysActive(self, entity_id):
        self._sprites[entity_id].removeAlwaysActive()

    def setSpriteVisible(self, entity_id):
        self._sprites[entity_id].setVisible()

    def setSpriteInvisible(self, entity_id):
        self._sprites[entity_id].setInvisible()

    def setSpriteEthereal(self, entity_id):
        self._sprites[entity_id].setEthereal()

    def setSpriteTangible(self, entity_id):
        self._sprites[entity_id].setTangible()

    #Returns true if sprite or it's dependants/clones are in an active cell
    def spriteIsInActiveCell(self, entity_id):
        return self._sprites[entity_id].renderNetworkInActiveCell()

    def getWorldSize(self):
        return self.world_size

    def getTileSize(self):
        return self.tile_size

    def getCellSize(self):
        return self.cell_size

    #layer_types is a list of enums which indicate which layers we should include
    #if that list is empty, just return all of the ids
    #Testing Function
    def getLayerIds(self, layer_types):
        layer_ids = list()
        for layer_id, scene_layer in self._scene_layers.items():
            if not layer_types or scene_layer.layer_type in layer_types:
                layer_ids.append(layer_id)
        return layer_ids

    def update(self):
        #First update the master grid to update the camera/cells
        self._scene_master_grid.update()
        for scene_layer in self._scene_layers.values():
            scene_layer.update()
