import pygame
from input_handler import InputHandler, InputManager
from input_handler import entity_input_map, debugger_input_map, camera_input_map
from input_handler import entity_key_state, debug_key_state, camera_key_state
from event_handler import EventHandler
from component_entity_physics import PhysicsComponentSystem
from component_entity_behavior import BehaviorComponentSystem
from behavior_states import BehaviorStateBase, CameraIdle
from component_entity_sprite import SpriteComponentSystem, EntitySpriteComponent
from component_scene_panorama import PanoramaComponentSystem
from component_scene_tilemap import TilemapComponentSystem
from render import SceneHandler
from game_states import StateStack, GameStateBase
from resource_management import ResourceManager, SpriteImageManager
from resource_management_entity import EntityResourceManager, ERESOURCE_DATA_TYPE, EntityResourceFactory
from resource_management_scene import SceneResourceManager, SRESOURCE_DATA_TYPE, \
    TiledXmlHandler, AtlasXmlHandler, AtlasJsonParser, SceneJsonParser
from debug import DebugHandler
from component_system import Component
import sys
sys.path.append("parameters\\")
import GRAPHICS_PARAM, FUNCTIONAL_PARAM

class GameEngineBuilder:
    def __init__(self):
        pass

    def buildBehaviorComponentSystem(self):
        return BehaviorComponentSystem()

    def buildEntityResourceManager(self):
        return EntityResourceManager()

    def buildEventHandler(self, initial_game_state):
        return EventHandler(current_game_state = initial_game_state)

    def buildGameStates(self):
        game_state_base = GameStateBase()
        game_states = list()
        game_states.append(game_state_base)
        return game_states

    def buildGameStateStack(self, initial_game_state):
        game_state_stack = StateStack(initial_state = initial_game_state,
                                      max_size = FUNCTIONAL_PARAM.MAX_STATE_STACK)
        return game_state_stack

    def buildInputManager(self, behavior_component_system, debug_handler):
        # We are hard coding the entity ids here, but in practice will aquire them by their e_tag_ids
        player1_input_handler = InputHandler(component_id=0,  # hardcoded - first entity is 0
                                             is_active=True,
                                             is_blocking=False,
                                             is_consumer=True,
                                             input_map=entity_input_map,
                                             key_state=entity_key_state,
                                             send_input=behavior_component_system.updateControlInputState,
                                             successor=None)

        camera_input_handler = InputHandler(component_id=1,  # hardcoded - second entity is 1
                                            is_active=True,
                                            is_blocking=False,
                                            is_consumer=True,
                                            input_map=camera_input_map,
                                            key_state=camera_key_state,
                                            send_input=behavior_component_system.updateControlInputState,
                                            successor=player1_input_handler)

        debug_input_handler = InputHandler(component_id=0,  # this is a don't care right now
                                           is_active=True,
                                           is_blocking=False,
                                           is_consumer=True,
                                           input_map=debugger_input_map,
                                           key_state=debug_key_state,
                                           send_input=debug_handler.updateControlInputState,
                                           successor=camera_input_handler)

        input_handlers = [debug_input_handler, camera_input_handler, player1_input_handler]
        input_manager = InputManager(input_handlers)
        return input_manager

    def buildPanoramaComponentSystem(self):
        return PanoramaComponentSystem()

    def buildPhysicsComponentSystem(self):
        return PhysicsComponentSystem()

    def buildSpriteImageManager(self):
        return SpriteImageManager()

    def buildSceneHandler(self, window):
        return SceneHandler(window=window)

    def buildSceneResourceManager(self):
        return SceneResourceManager()

    def buildSpriteComponentSystem(self):
        return SpriteComponentSystem()

    def buildTilemapComponentSystem(self):
        return TilemapComponentSystem()

    def buildWindow(self):
        return pygame.display.set_mode((GRAPHICS_PARAM.WINDOW_SIZE[0], GRAPHICS_PARAM.WINDOW_SIZE[1]), #window size
                                         pygame.DOUBLEBUF | pygame.HWSURFACE) #flags

    def setupBehaviorState(self, event_handler, physics_component_system):
        BehaviorStateBase.send_force = physics_component_system.receiveForce
        BehaviorStateBase.send_sound = None
        BehaviorStateBase.send_event = event_handler.receiveEvent
        BehaviorStateBase.get_position = physics_component_system.getPosition

    def setupCamera(self, scene_handler):
        CameraIdle.observer_methods.append(scene_handler.receiveCameraOffset)

    def setupComponent(self, scene_handler):
        Component.request_ptr = scene_handler.requestPtr

    def setupDebugHandler(self, game_engine):
        DebugHandler.change_game_speed = game_engine.debugChangeGameSpeed
        DebugHandler.pause_game = game_engine.pause  # toggles pause

    def setupEntityResourceManager(self, load_sprite_data, sprite_component_system, physics_component_system,
                                   behavior_component_system):
        EntityResourceFactory.load_sprite_data = load_sprite_data
        #create_component_methods
        EntityResourceManager.create_component_methods[ERESOURCE_DATA_TYPE.SPRITE] = sprite_component_system.createComponent
        EntityResourceManager.create_component_methods[ERESOURCE_DATA_TYPE.PHYSICS] = physics_component_system.createComponent
        EntityResourceManager.create_component_methods[ERESOURCE_DATA_TYPE.BEHAVIOR] = behavior_component_system.createComponent
        #get_component_ptr_methods
        EntityResourceManager.get_component_ptr_methods[ERESOURCE_DATA_TYPE.PHYSICS] = sprite_component_system.getSceneComponents
        EntityResourceManager.get_component_ptr_methods[ERESOURCE_DATA_TYPE.SPRITE] = physics_component_system.getSceneComponents
        EntityResourceManager.get_component_ptr_methods[ERESOURCE_DATA_TYPE.BEHAVIOR] = behavior_component_system.getSceneComponents
        #call_request_pointers_methods
        EntityResourceManager.call_request_pointers_methods[ERESOURCE_DATA_TYPE.BEHAVIOR] = behavior_component_system.requestPointers
        EntityResourceManager.call_request_pointers_methods[ERESOURCE_DATA_TYPE.PHYSICS] = physics_component_system.requestPointers
        EntityResourceManager.call_request_pointers_methods[ERESOURCE_DATA_TYPE.SPRITE] = sprite_component_system.requestPointers

    def setupGameStates(self, s_resource_manager, e_resource_manager, scene_layer_manager, physics_component_system,
                        behavior_component_system, sprite_component_system):
        GameStateBase.call_spawn_scene = s_resource_manager.spawnScene
        GameStateBase.call_spawn_entity = e_resource_manager.spawnEntity
        GameStateBase.add_entity_renderable = scene_layer_manager.addSceneComponent
        GameStateBase.call_set_entity_position = physics_component_system.setPosition
        GameStateBase.call_set_entity_velocity = physics_component_system.setVelocity
        GameStateBase.call_set_entity_acceleration = physics_component_system.setAcceleration
        GameStateBase.call_set_entity_orientation = physics_component_system.setOrientation
        GameStateBase.call_set_behavior_state = behavior_component_system.setBehaviorState
        GameStateBase.call_set_entity_tag = e_resource_manager.setTagId
        GameStateBase.call_set_scene_tag = s_resource_manager.setTagId
        call_remove_component_list = list()
        call_remove_component_list.append(physics_component_system.removeComponent)
        call_remove_component_list.append(behavior_component_system.removeComponent)
        call_remove_component_list.append(sprite_component_system.removeComponent)
        GameStateBase.call_remove_component_list = tuple(call_remove_component_list)

    def setupPanoramaComponentSystem(self):
        pass

    def setupRenderLayer(self):
        pass

    def setupResourceManager(self, add_component_to_layer):
        ResourceManager.add_component_to_layer = add_component_to_layer

    def setupSpriteClasses(self, physics_component_system, behavior_component_system):
        SpriteComponentSystem.receive_behavior_state_ptrs = behavior_component_system.getBehaviorStates
        SpriteComponentSystem.receive_particle_ptrs = physics_component_system.getParticlePtrs
        EntitySpriteComponent.set_behavior_state_frame_times = behavior_component_system.setBehaviorStateFrameTimes

    def setupSceneLayer(self):
        pass

    def setupSceneResourceManager(self, load_panorama_image, load_atlas_image, create_scene_layer, panorama_component_system, tilemap_component_system):
        TiledXmlHandler.load_panorama_image = load_panorama_image
        AtlasXmlHandler.load_atlas_image = load_atlas_image
        SceneJsonParser.load_panorama_image = load_panorama_image
        AtlasJsonParser.load_atlas_image = load_atlas_image
        SceneResourceManager.create_scene_layer = create_scene_layer
        SceneResourceManager.create_atlas = tilemap_component_system.createAtlas
        SceneResourceManager.create_component_methods[SRESOURCE_DATA_TYPE.PANORAMA] = panorama_component_system.createComponent
        SceneResourceManager.get_scene_component_methods[SRESOURCE_DATA_TYPE.PANORAMA] = panorama_component_system.getSceneComponents
        SceneResourceManager.create_component_methods[SRESOURCE_DATA_TYPE.TILEMAP] = tilemap_component_system.createComponent
        SceneResourceManager.get_scene_component_methods[SRESOURCE_DATA_TYPE.TILEMAP] = tilemap_component_system.getSceneComponents

    def setupSceneHandler(self):
        pass

    def setupTilemapComponentSystem(self):
        pass
