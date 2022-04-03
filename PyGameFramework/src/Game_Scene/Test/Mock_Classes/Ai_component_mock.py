class AiComponentMock:
    def __init__(self,
                 entity_id):
        self._entity_id = entity_id

    def getEntityId(self):
        return self._entity_id

    def update(self):
        pass

class AiComponentSystemMock:
    def __init__(self):
        self._active_ai_components = dict()# {(int)entity_id : AiComponentMock}
        self._inactive_ai_components = dict()# {(int)entity_id : AiComponentMock}

        self._entity_manager = None #Get the active entity_ids from here
        self._onscreen_entity_ids = None  # shortcut to freqeuently accessed list

    def setEntityManager(self, entity_manager):
        self._entity_manager = entity_manager
        self._onscreen_entity_ids = self._entity_manager._onscreen_entity_ids

    def addAiComponent(self, entity_id, ai_component, active=True):  # int, AiComponentMock, bool
        try:
            if active:
                self._active_ai_components[entity_id] = ai_component
            else:
                self._inactive_ai_components[entity_id] = ai_component
        except Exception as e:
            print("Exception caught during AiComponentSystemMock.addAiComponent(): " + str(e))
            return False
        return True

    def removeAiComponent(self, entity_id):
        try:
            del (self._active_ai_components[entity_id])
        except:
            try:
                del (self._inactive_ai_components[entity_id])
            except:
                return False
        return True

    def activateAiComponent(self, entity_id):  # int
        try:
            self._active_ai_components[entity_id] = self._inactive_ai_components[entity_id]
            del (self._inactive_ai_components[entity_id])
        except:
            return False
        return True

    def deactivateAiComponent(self, entity_id):  # int
        try:
            self._inactive_ai_components[entity_id] = self._active_ai_components[entity_id]
            del (self._active_ai_components[entity_id])
        except:
            return False
        return True

    def update(self):
        try:
            for entity_id in self._entity_manager._onscreen_entity_ids.keys():
                try:
                    self._active_ai_components[entity_id].update
                except:
                    pass
        except Exception as e:
            print("Exception caught during AiComponentSystemMock.update(): " + str(e))
            return False
        return True

class AiSceneManager:
    def __init__(self):
        self._ai_component_systems = dict() #{scene_id : AiComponentSystemMock}
        self._active_component_systems = dict()

    def addAiComponentSystem(self, scene_id, ai_component_system):
        self._ai_component_systems[scene_id] = ai_component_system

    def removeAiComponentSystem(self, scene_id):
        try:
            del(self._ai_component_systems[scene_id])
            del(self._active_component_systems[scene_id])
        except:
            pass

    def activateAiComponentSystem(self, scene_id):
        try:
            self._active_component_systems[scene_id] = self._ai_component_systems[scene_id]
        except Exception as e:
            print("Exception caught during AiSceneManager.activateAiComponentSystem(): " + str(e))
            return False

    def deactivateAiComponentSystem(self, scene_id):
        try:
            del(self._active_component_systems[scene_id])
        except:
            pass

    def addAiComponent(self, scene_id, entity_id, ai_component, active = True):  # int, AiComponentMock, bool
        self._ai_component_systems[scene_id].addAiComponent(entity_id, ai_component, active)

    def removeAiComponent(self, entity_id, scene_id):
        self._ai_component_systems[scene_id].removeAiComponent(entity_id)

    def update(self):
        try:
            for component_system in self._active_component_systems.values():
                component_system.update()
        except Exception as e:
            print("Exception caught during AiSceneManager.update(): " + str(e))
            return False
        return True






