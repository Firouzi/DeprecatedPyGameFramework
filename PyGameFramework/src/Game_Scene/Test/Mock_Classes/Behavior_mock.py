from Game_Scene.Test.Mock_Classes.Grid_utility_mock import MockFlag

class BehaviorFSMMock:
    def __init__(self,
                 entity_id):
        self.entity_id = entity_id

        self._behavior_state = 1
        self.state_has_changed = MockFlag()
        self.animation_has_flipped = MockFlag()
        self.frame = 0
        self.numb_frames = 3

    def getEntityId(self):
        return self.entity_id

    def getBehaviorState(self):
        return self._behavior_state

    def setBehaviorState(self, behavior_state): #int
        self._behavior_state = behavior_state
        self.state_has_changed.value = True

    def update(self):
        pass

    #Normally this fips on a timer
    def flipAnimation(self):
        self.animation_has_flipped.value = True
        self.frame += 1
        if self.frame >= self.numb_frames:
            self.frame = 0

class BehaviorComponentSystemMock:
    def __init__(self):
        self._active_behaviorFSMs = dict()  # {(int)entity_id : BehaviorFSM}
        self._inactive_behaviorFSMs = dict()

        self._entity_manager = None #Get the active entity_ids from here
        self._onscreen_entity_ids = None  # shortcut to freqeuently accessed list

    def setEntityManager(self, entity_manager):
        self._entity_manager = entity_manager
        self._onscreen_entity_ids = self._entity_manager._onscreen_entity_ids

    def activateBehaviorFSM(self, entity_id):  # int
        try:
            self._active_behaviorFSMs[entity_id] = self._inactive_behaviorFSMs[entity_id]
            del (self._inactive_behaviorFSMs[entity_id])
        except:
            return False
        return True

    def deactivateBehaviorFSM(self, entity_id):  # int
        try:
            self._inactive_behaviorFSMs[entity_id] = self._active_behaviorFSMs[entity_id]
            del (self._active_behaviorFSMs[entity_id])
        except:
            return False
        return True

    def flipAnimation(self, entity_id):
        try:
            if self._onscreen_entity_ids.get(entity_id) is not None:
                self._active_behaviorFSMs[entity_id].flipAnimation()
        except:
            try:
                self._inactive_behaviorFSMs[entity_id].flipAnimation()
            except:
                return False
        return True

    def setBehaviorState(self, entity_id, behavior_state_id):
        try:
            if self._onscreen_entity_ids.get(entity_id) is not None:
                self._active_behaviorFSMs[entity_id].setBehaviorState(behavior_state_id)
        except:
            try:
                self._inactive_behaviorFSMs[entity_id].setBehaviorState(behavior_state_id)
            except:
                return False
        return True

    def addBehaviorFSM(self, entity_id, behaviorFSM, active=True):  # int, BehaviorFSMMock, bool
        try:
            if active:
                self._active_behaviorFSMs[entity_id] = behaviorFSM
            else:
                self._inactive_behaviorFSMs[entity_id] = behaviorFSM
        except Exception as e:
            print("Exception caught during BehaviorComponentSystemMock.addBehaviorFSM(): " + str(e))
            return False
        return True

    def removeBehaviorFSM(self, entity_id):
        try:
            del (self._active_behaviorFSMs[entity_id])
        except:
            try:
                del (self._inactive_behaviorFSMs[entity_id])
            except:
                return False
        return True

    def update(self):
        try:
            for entity_id in self._entity_manager._onscreen_entity_ids.keys():
                try:
                    self._active_behaviorFSMs[entity_id].update
                except:
                    pass
        except Exception as e:
            print("Exception caught during BehaviorComponentSystemMock.update(): " + str(e))
            return False
        return True

class BehaviorSceneManager:
    def __init__(self):
        self._behavior_component_systems = dict() #{scene_id : behavior_component_systems}
        self._active_component_systems = dict() #references to elements in_behavior_component_systems

    def addBehaviorComponentSystem(self, scene_id, behavior_component_system):
        self._behavior_component_systems[scene_id] = behavior_component_system

    def removeBehaviorComponentSystem(self, scene_id):
        try:
            del (self._behavior_component_systems[scene_id])
            del (self._active_component_systems[scene_id])
        except:
            pass

    def activateBehaviorComponentSystem(self, scene_id):
        try:
            self._active_component_systems[scene_id] = self._behavior_component_systems[scene_id]
        except Exception as e:
            print("Exception caught during BehaviorSceneManager.activateBehaviorComponentSystem(): " + str(e))
            return False

    def deactivateBehaviorComponentSystem(self, scene_id):
        try:
            del(self._active_component_systems[scene_id])
        except:
            pass

    def addBehaviorFSM(self, scene_id, entity_id, behaviorFSM, active=True):
        self._behavior_component_systems[scene_id].addBehaviorFSM(entity_id, behaviorFSM, active)

    def removeBehaviorFSM(self, entity_id, scene_id):
        self._behavior_component_systems[scene_id].removeBehaviorFSM(entity_id)

    def flipAnimation(self, entity_id, scene_id):
        try:
            # no action taken if the scene is not active
            self._active_component_systems[scene_id].flipAnimation(entity_id)
        except:
            pass

    def setBehaviorState(self, entity_id, behavior_state_id, scene_id):
        try:
            # no action taken if the scene is not active
            self._active_component_systems[scene_id].setBehaviorState(entity_id, behavior_state_id)
        except:
            pass

    def update(self):
        try:
            for component_system in self._active_component_systems.values():
                component_system.update()
        except Exception as e:
            print("Exception caught during BehaviorSceneManager.update(): " + str(e))
            return False
        return True
