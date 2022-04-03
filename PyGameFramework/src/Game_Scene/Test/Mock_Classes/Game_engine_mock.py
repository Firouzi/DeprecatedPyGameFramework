from Game_Scene.Test.Mock_Classes.Ai_component_mock import AiComponentSystemMock, AiComponentMock, AiSceneManager
from Game_Scene.Test.Mock_Classes.Behavior_mock import BehaviorComponentSystemMock, BehaviorFSMMock, BehaviorSceneManager
from Entity_manager import EntitySystem, EntitySceneManager
from Game_Scene.Test.Mock_Classes.Physics_mock import ParticleComponentSystemMock, ParticleMock, PhysicsSceneManager
from Scene_Node.Sprite_node import SpriteNode
from Game_Scene.Scene_Manager.Scene_camera import CameraManager
#Sprite States
from Sprite_state_active import SpriteStateActive
from Sprite_state_inv import SpriteStateActiveInvisible
from Sprite_state_AA import SpriteStateAlwaysActive
from Sprite_state_AA_inv import SpriteStateAlwaysActiveInvisible
from Sprite_state_ether import SpriteStateEthereal
from Sprite_state_inv_ether import SpriteStateInvisibleEthereal
from Sprite_state_AA_ether import SpriteStateAlwaysActiveEthereal
from Sprite_state_AA_inv_ether import SpriteStateAlwaysActiveInvisibleEthereal
from Sprite_state_deactivated import SpriteStateDeactivated, \
    SpriteStateInvisibleDeactivated, SpriteStateAlwaysActiveDeactivated, SpriteStateAlwaysActiveInvisibleDeactivated, \
    SpriteStateEtherealDeactivated, SpriteStateInvisibleEtherealDeactivated, \
    SpriteStateAlwaysActiveEtherealDeactivated, SpriteStateAlwaysActiveInvisibleEtherealDeactivated
import Sprite_state
from Game_Scene.Scene_Manager.Scene_manager import SceneManager
from Game_Scene.Scene_Manager.Scene import Scene

class GameEngineMock:
    #the resource_id is the index
    #The image coordinates define the coarse bounding box
    SRITE_DATA_MOCK = [{'state_images': {1: None, 2: None, 3: None}, #sprite resource id 0
                        # Set of frames mapped to a behavior id
                           'imagecoordinateslists': {1: [[0,0,12,12], [12,0,25,8], [27,0,11,21]],
                                                     2: [[0,3,5,6], [5,4,5,4], [10,5,4,9]],
                                                     3: [[3,4,62,8], [65,12,12,55], [77,67,93,106]]}},
                       {'state_images': {1: None, 2: None, 3: None}, #sprite resource id 1
                           'imagecoordinateslists': {1: [[0,0,3,3], [3,0,3,3], [6,0,3,3]],
                                                     2: [[0,0,3,3], [3,0,3,3], [6,0,3,3]],
                                                     3: [[0,0,3,3], [3,0,3,3], [6,0,3,3]]}},
                       {'state_images': {1: None, 2: None, 3: None}, #sprite resource id 2
                           'imagecoordinateslists': {1: [[0,0,3,3], [3,0,3,3], [6,0,3,3]],
                                                     2: [[0,0,3,3], [3,0,3,3], [6,0,3,3]],
                                                     3: [[0,0,3,3], [3,0,3,3], [6,0,3,3]]}}]

    def __init__(self):
        #Testing lists - tracking expected IDs
        self._scene_ids = None #The _scene_ids and _active_scene_ids were created for testing...
        self._active_scene_ids = None #...but they may ultimately be needed anyways
        self._testing_layer_ids = None #dict ({scene_id : list(layer_ids))
        #This list is maintainted externally by the Game_engine_testing_system
        #Store the lists by scene_id, so that they can be cleared at once when a scene is removed
        #This is only used for testing not the actual engine functionality
        self.testing_system_entity_ids = None #{scene_id : entity_ids}
        #use this to pass in the set of booleans releated to sprite state and get the corresponding state
        self.sprite_state_map = dict() #{[active, ethereal, always_active, visible] : SpriteState}

        self._camera_manager = None
        self._scene_manager = None
        self._physics_scene_manager = None
        self._behavior_scene_manager = None
        self._ai_scene_manager = None
        self._entity_scene_manager = None

        self._initializeSpriteStates()
        self._initializeSystems()

    #For testing system use - returns the scene ID that an entity id belongs to
    def getEntitySceneId(self, entity_id):
        for scene_id, entity_ids in self.testing_system_entity_ids.items():
            if entity_id in entity_ids:
                return scene_id
        return 0 # failed to find the entity_id

    #For testing system use, return all current scene_ids
    def getSceneIds(self):
        return self._scene_ids

    # For testing system use
    def getActiveSceneIds(self):
        return self._scene_manager.getActiveSceneIds()

    # For testing system use
    def getInactiveSceneIds(self):
        return self._scene_manager.getInactiveSceneIds()

    #For testing
    def getCameraIds(self):
        return self._camera_manager.getCameraIds()

    #For testing system use, return all current layer_ids of passed in types
    #if types is an empty list, then return all layer ids
    def getLayerIds(self, scene_id, layer_types = tuple()):
        return self._scene_manager.getLayerIds(scene_id, layer_types)

    # testing function
    def addTestingEntityId(self, scene_id, entity_id):
        try:
            self.testing_system_entity_ids[scene_id].append(entity_id)
        except:
            print("Non existing scene_id",scene_id)

    #testing function - find the list that holds the entity_id and remove that entity_id
    def removeTestingEntityId(self, entity_id):
        try:
            for scene_id, entity_list in self.testing_system_entity_ids.items():
                if entity_id in entity_list:
                    entity_list.remove(entity_id)
                    return
        except:
            print("Failed to remove entity_id",entity_id)

    #testing function - returns a flat list of all the available entity_ids
    def getAllTestingEntityIds(self):
        all_entity_ids = list()
        for entity_list in self.testing_system_entity_ids.values():
            for entity_id in entity_list:
                all_entity_ids.append(entity_id)
        return all_entity_ids

    #testing function - returns a flat dict of entity_id: sprite
    def getAllSprites(self):
        return self._scene_manager.getAllSprites()

    #testing function
    def getSceneWorldSize(self, scene_id):
        return self._scene_manager._scenes[scene_id].world_size

    #Removes all entities and creates a new grid
    #uses last updated PARAMS, which are locked in until the next initialization
    def resetEngine(self):
        self._initializeSystems()

    #The sprite states are static, only one copy needed as the states themselves do not store any state data
    def _initializeSpriteStates(self):
        #active
        Sprite_state.SPRITE_STATE_ACTIVE = SpriteStateActive()
        Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE = SpriteStateActiveInvisible()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE = SpriteStateAlwaysActive()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE = SpriteStateAlwaysActiveInvisible()
        #active ethereal
        Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL = SpriteStateEthereal()
        Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL = SpriteStateInvisibleEthereal()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL = SpriteStateAlwaysActiveEthereal()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL = SpriteStateAlwaysActiveInvisibleEthereal()
        #deactivated
        Sprite_state.SPRITE_STATE_DEACTIVATED = SpriteStateDeactivated()
        Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED = SpriteStateInvisibleDeactivated()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED = SpriteStateAlwaysActiveDeactivated()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED = SpriteStateAlwaysActiveInvisibleDeactivated()
        #deactivated ethereal
        Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED = SpriteStateEtherealDeactivated()
        Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED = SpriteStateInvisibleEtherealDeactivated()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED = SpriteStateAlwaysActiveEtherealDeactivated()
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED = \
            SpriteStateAlwaysActiveInvisibleEtherealDeactivated()
        #When a sprite is deactivated, the current state changes to it's deactivated version, stored in the state
        Sprite_state.SPRITE_STATE_ACTIVE.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_DEACTIVATED
        Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED
        #ethereal
        Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED
        Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED
        Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL.deactivated_sprite_state = \
            Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED

        self.sprite_state_map = dict() #{[active, ethereal, always_active, visible] : SpriteState}
        self.sprite_state_map[True, True, True, True] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL
        self.sprite_state_map[True, True, True, False] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL
        self.sprite_state_map[True, True, False, True] = Sprite_state.SPRITE_STATE_ACTIVE_ETHEREAL
        self.sprite_state_map[True, True, False, False] = Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

        self.sprite_state_map[True, False, True, True] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE
        self.sprite_state_map[True, False, True, False] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE
        self.sprite_state_map[True, False, False, True] = Sprite_state.SPRITE_STATE_ACTIVE
        self.sprite_state_map[True, False, False, False] = Sprite_state.SPRITE_STATE_ACTIVE_INVISIBLE

        self.sprite_state_map[False, True, True, True] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED
        self.sprite_state_map[False, True, True, False] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED
        self.sprite_state_map[False, True, False, True] = Sprite_state.SPRITE_STATE_ETHEREAL_DEACTIVATED
        self.sprite_state_map[False, True, False, False] = Sprite_state.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

        self.sprite_state_map[False, False, True, True] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED
        self.sprite_state_map[False, False, True, False] = Sprite_state.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED
        self.sprite_state_map[False, False, False, True] = Sprite_state.SPRITE_STATE_DEACTIVATED
        self.sprite_state_map[False, False, False, False] = Sprite_state.SPRITE_STATE_INVISIBLE_DEACTIVATED

    def _initializeSystems(self):
        self._scene_ids = list()
        self._active_scene_ids = list()
        self._testing_layer_ids = dict()
        self.testing_system_entity_ids = dict()

        self._camera_manager = CameraManager()
        self._scene_manager = SceneManager()
        self._entity_scene_manager = EntitySceneManager()
        self._physics_scene_manager = PhysicsSceneManager()
        self._behavior_scene_manager = BehaviorSceneManager()
        self._ai_scene_manager = AiSceneManager()

    #Adds a new scene (does not activate it)
    def createScene(self,
                    world_size,
                    cell_size,
                    tile_size):
        new_scene_id = self._scene_manager.generateSceneId()
        sprite_scene = Scene(new_scene_id,
                             world_size,
                             cell_size,
                             tile_size)
        particle_component_system = ParticleComponentSystemMock(world_size)
        behavior_component_system = BehaviorComponentSystemMock()
        ai_component_system = AiComponentSystemMock()
        entity_manager = EntitySystem(particle_component_system,
                                      behavior_component_system,
                                      ai_component_system,
                                      sprite_scene)
        ai_component_system.setEntityManager(entity_manager)
        behavior_component_system.setEntityManager(entity_manager)
        particle_component_system.setEntityManager(entity_manager)
        sprite_scene.setMasterGridNotify(entity_manager.notifySpriteOnScreen,
                                         entity_manager.notifySpriteOffScreen)
        self.testing_system_entity_ids[new_scene_id] = list()
        self._scene_manager.addScene(new_scene_id, sprite_scene)
        self._entity_scene_manager.addEntityManager(new_scene_id, entity_manager)
        self._physics_scene_manager.addParticleComponentSystem(new_scene_id, particle_component_system)
        self._behavior_scene_manager.addBehaviorComponentSystem(new_scene_id, behavior_component_system)
        self._ai_scene_manager.addAiComponentSystem(new_scene_id, ai_component_system)
        self._scene_ids.append(new_scene_id)
        self._testing_layer_ids[new_scene_id] = list()

        return new_scene_id

    def activateScene(self, scene_id):
        if scene_id not in self._active_scene_ids:
            self._active_scene_ids.append(scene_id)
        self._scene_manager.activateScene(scene_id)
        self._physics_scene_manager.activateParticleComponentSystem(scene_id)
        self._behavior_scene_manager.activateBehaviorComponentSystem(scene_id)
        self._ai_scene_manager.activateAiComponentSystem(scene_id)
        self._entity_scene_manager.activateEntityManager(scene_id)

    def deactivateScene(self, scene_id):
        try:
            self._active_scene_ids.remove(scene_id)
        except:
            pass
        self._scene_manager.deactivateScene(scene_id)
        self._physics_scene_manager.deactivateParticleComponentSystem(scene_id)
        self._behavior_scene_manager.deactivateBehaviorComponentSystem(scene_id)
        self._ai_scene_manager.deactivateAiComponentSystem(scene_id)
        self._entity_scene_manager.deactivateEntityManager(scene_id)

    def removeScene(self, scene_id):
        if scene_id in self._active_scene_ids:
            print("Tried to remove an activated scene, which I've decided is illegal: ", scene_id)
            assert False
        try:
            self._scene_ids.remove(scene_id)
        except:
            pass
        try:
            #all of these entity ids are now removed
            del(self.testing_system_entity_ids[scene_id])
        except:
            pass
        try:
            del(self._testing_layer_ids[scene_id])
        except:
            pass
        #Need to tell the entity manager what entities and scene are removed
        entity_ids = self._scene_manager.removeScene(scene_id)
        self._physics_scene_manager.removeParticleComponentSystem(scene_id)
        self._behavior_scene_manager.removeBehaviorComponentSystem(scene_id)
        self._ai_scene_manager.removeAiComponentSystem(scene_id)
        self._entity_scene_manager.removeEntityManager(scene_id, entity_ids)
        #Any cameras attached to the scene are detached, but not removed
        self._camera_manager.sceneRemovedFromCamera(scene_id)

    #returns the id for the created camera
    def createCamera(self,
                     window_size,
                     activate_range,
                     deactivate_range):
        return self._camera_manager.createCamera(window_size,
                                                 activate_range,
                                                 deactivate_range)

    def removeCamera(self, camera_id):
        self._camera_manager.removeCamera(camera_id)

    def attachCamera(self, scene_id, camera_id, position):
        camera = self._camera_manager.getCamera(camera_id)
        self._scene_manager.attachCamera(scene_id, camera_id, camera, position)

    def detachCamera(self, camera_id):
        self._camera_manager.detachCamera(camera_id)

    def getCameraWindowSize(self, camera_id):
        return self._camera_manager.getCameraWindowSize(camera_id)

    def setCameraWindowSize(self, camera_id, window_size):
        self._camera_manager.setWindowSize(camera_id, window_size)

    def createSceneLayer(self, scene_id, layer_id, layer_type = 1):
        self._scene_manager.createSceneLayer(scene_id, layer_id, layer_type)
        self._testing_layer_ids[scene_id].append(layer_id)

    def removeSceneLayer(self, scene_id, layer_id):
        remove_ids = self._scene_manager.getEntityIdsFromLayer(scene_id, layer_id)
        for entity_id in remove_ids:
            self.removeNode(entity_id)
        self._scene_manager.removeSceneLayer(scene_id, layer_id)
        self._testing_layer_ids[scene_id].remove(layer_id)

    def spawnEntity(self,
                    scene_id,
                    layer_id,
                    position,
                    resource_id_mock, #resource_id_mock is a key to a simple dict that holds some meta data
                    active = True,
                    physics_active = True,
                    behavior_active = True,
                    ai_active = True,
                    visible = True,
                    ethereal = False,
                    always_active = False):
        world_size =  self._scene_manager._scenes[scene_id].world_size
        resource_data = GameEngineMock.SRITE_DATA_MOCK[resource_id_mock]
        entity_id = self._entity_scene_manager.generateEntityId()
        particle = ParticleMock(entity_id, [position[0],position[1], position[2]], world_size) #make sure not to send unintended ref
        behaviorFsm = BehaviorFSMMock(entity_id)
        aiComponent = AiComponentMock(entity_id)
        current_sprite_state = self.sprite_state_map[active, ethereal, always_active, visible]
        sprite = SpriteNode(entity_id,
                            particle,
                            behaviorFsm,
                            resource_data['state_images'],
                            resource_data['imagecoordinateslists'],
                            current_sprite_state)
        #Need to initially add the components to the active or inactive lists, depending on initial state
        self._addParticle(scene_id, entity_id, particle, (physics_active|always_active))
        self._addBehaviorFSM(scene_id, entity_id, behaviorFsm, (behavior_active|always_active))
        self._addAiComponent(scene_id, entity_id, aiComponent, (ai_active|always_active))
        #Entity manager just accepts the initial state
        self._entity_scene_manager.addEntityStatus(scene_id = scene_id,
                                                   layer_id = layer_id,
                                                   entity_id=entity_id,
                                                   active = active,
                                                   always_active = always_active,
                                                   sprite_visible = visible,
                                                   sprite_ethereal = ethereal,
                                                   physics_active = (physics_active|always_active),
                                                   behavior_active = (behavior_active|always_active),
                                                   ai_active = (ai_active|always_active))
        #We set the status as desired and then add the sprite - sprite will send updates to EM as needed
        #Will assume 'onscreen' to start.  If sprite is offscreen, send the update to the EM upon insert.
        self._addNode(scene_id, layer_id, entity_id, sprite)

        return entity_id

    def _addParticle(self, scene_id, entity_id, particle, active = True):
        self._physics_scene_manager.addParticle(scene_id, entity_id, particle, active)

    def _addBehaviorFSM(self, scene_id, entity_id, behaviorFSM, active = True):
        self._behavior_scene_manager.addBehaviorFSM(scene_id, entity_id, behaviorFSM, active)

    def _addAiComponent(self, scene_id, entity_id, aiComponent, active = True):
        self._ai_scene_manager.addAiComponent(scene_id, entity_id, aiComponent, active)

    def _addNode(self, scene_id, layer_id, entity_id, sprite):
        self._scene_manager.addNode(scene_id, layer_id, entity_id, sprite)

    def activateEntity(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.activateEntity(entity_id, scene_id)

    def deactivateEntity(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.deactivateEntity(entity_id, scene_id)

    def setEntityAlwaysActive(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.setEntityAlwaysActive(entity_id, scene_id)

    def setEntitySpriteVisible(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.setEntitySpriteVisible(entity_id, scene_id)

    def setSpriteInvisible(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.setSpriteInvisible(entity_id, scene_id)

    def setSpriteEthereal(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.setSpriteEthereal(entity_id, scene_id)

    def setSpriteTangible(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.setSpriteTangible(entity_id, scene_id)

    def activateEntityPhysics(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.activateEntityPhysics(entity_id, scene_id)

    def activateEntityBehavior(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.activateEntityBehavior(entity_id, scene_id)

    def activateEntityAi(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.activateEntityAi(entity_id, scene_id)

    def removeEntityAlwaysActive(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.removeEntityAlwaysActive(entity_id, scene_id)

    def deactivateEntityPhysics(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.deactivateEntityPhysics(entity_id, scene_id)

    def deactivateEntityBehavior(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.deactivateEntityBehavior(entity_id, scene_id)

    def deactivateEntityAI(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.deactivateEntityAI(entity_id, scene_id)

    def addEntityDependancy(self, entity_id, dependant_entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.addEntityDependancy(entity_id, dependant_entity_id, scene_id)

    def removeEntityDependancy(self, entity_id, dependant_entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._entity_scene_manager.removeEntityDependancy(entity_id, dependant_entity_id, scene_id)

    #should be "remove entity" - should the EM be handing this completely?   Solve that later...
    def removeNode(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._scene_manager.removeNode(entity_id, scene_id)
        self._physics_scene_manager.removeParticle(entity_id, scene_id)
        self._behavior_scene_manager.removeBehaviorFSM(entity_id, scene_id)
        self._ai_scene_manager.removeAiComponent(entity_id, scene_id)
        self._entity_scene_manager.removeEntity(entity_id, scene_id)
        self.removeTestingEntityId(entity_id)

    def panSprite(self, entity_id, pan):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._physics_scene_manager.panParticle(entity_id, [pan[0], pan[1],pan[2]], scene_id) #make sure not to send unintended ref

    def moveSprite(self, entity_id, move):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._physics_scene_manager.moveParticle(entity_id, [move[0], move[1],move[2]], scene_id) #make sure not to send unintended ref

    def flipAnimation(self, entity_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._behavior_scene_manager.flipAnimation(entity_id, scene_id)

    def setBehaviorState(self, entity_id, behavior_state_id):
        scene_id = self._entity_scene_manager.getEntitySceneLayer(entity_id)[0]
        self._behavior_scene_manager.setBehaviorState(entity_id, behavior_state_id, scene_id)

    def panCamera(self, camera_id, pan):
        self._camera_manager.panCamera(camera_id, pan)

    def moveCamera(self, camera_id, move):
        self._camera_manager.moveCamera(camera_id, move)

    #active_entity_ids is just a list of ints, entity_ids expected to be present
    def update(self):
        try:
            self._physics_scene_manager.update()
            self._behavior_scene_manager.update()
            self._ai_scene_manager.update()
            self._scene_manager.update()
        except Exception as e:
            print("Exception caught during main update loop in Game_engine_mock: ", e)
            assert False #Throw an exception to whoever wants it, things are going badly if we are here