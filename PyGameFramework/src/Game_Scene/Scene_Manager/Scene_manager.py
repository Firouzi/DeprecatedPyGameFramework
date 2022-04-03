class SceneManager:
    def __init__(self):
        self.next_scene_id = 0 #scene 0 is never used
        self._scenes = dict()
        #All active scenes will be updated on each loop
        self._active_scenes = dict()

    def generateSceneId(self):
        self.next_scene_id +=1 #so value 0 is never used
        return self.next_scene_id

    def addScene(self, scene_id, scene):
        self._scenes[scene_id] = scene

    #Removes thes scene, and returns the list of entity_id's that were part of that scene
    def removeScene(self, scene_id):
        entity_ids = self._scenes[scene_id].getEntityIds()
        try:
            del(self._scenes[scene_id])
            del(self._active_scenes[scene_id])
        except:
            pass
        return entity_ids

    def activateScene(self, scene_id):
        try:
            self._active_scenes[scene_id] = self._scenes[scene_id]
            self._active_scenes[scene_id].activateScene()
            return True
        except:
            return False

    def deactivateScene(self, scene_id):
        try:
            self._scenes[scene_id].deactivateScene()
            del(self._active_scenes[scene_id])
            return True
        except:
            return False

    def createSceneLayer(self, scene_id, layer_id, layer_type):
        self._scenes[scene_id].createSceneLayer(layer_id, layer_type)

    def getEntityIdsFromLayer(self, scene_id, layer_id):
        return self._scenes[scene_id].getEntityIdsFromLayer(layer_id)
    #Returns a list of entity_ids that have been removed as a result (this is possibly temp for testing)
    def removeSceneLayer(self, scene_id, layer_id):
        self._scenes[scene_id].removeSceneLayer(layer_id)

    def addNode(self, scene_id, layer_id, entity_id, node):
        self._scenes[scene_id].addNode(layer_id, entity_id, node)

    def removeNode(self, entity_id, scene_id):
        self._scenes[scene_id].removeNode(entity_id)

    def attachCamera(self, scene_id, camera_id, camera, position):
        self._scenes[scene_id].attachCamera(camera_id, camera, position)

    def detachCamera(self, scene_id, camera_id):
        self._scenes[scene_id].detachCamera(camera_id)

    # testing function
    def getLayerIds(self, scene_id, layer_types):
        return self._scenes[scene_id].getLayerIds(layer_types)

    # For testing system use
    def getActiveSceneIds(self):
        active_scene_ids = list()
        for scene_id in self._scenes.keys():
            if self._active_scenes.get(scene_id) is not None:
                active_scene_ids.append(scene_id)
        return active_scene_ids

    # For testing system use
    def getInactiveSceneIds(self):
        inactive_scene_ids = list()
        for scene_id in self._scenes.keys():
            if self._active_scenes.get(scene_id) is None:
                inactive_scene_ids.append(scene_id)
        return inactive_scene_ids

    #testing function - returns a flat dict of entity_id: sprite
    def getAllSprites(self):
        all_sprites = dict() #{entity_id : sprite}
        for scene in self._scenes.values():
            for entity_id, sprite in scene._sprites.items():
                all_sprites[entity_id] = sprite
        return all_sprites

    def update(self):
        for scene in self._active_scenes.values():
            scene.update()
