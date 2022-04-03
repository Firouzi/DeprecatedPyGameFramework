from Entity_manager import ACTIVATED_INDEX, ALWAYS_ACTIVE_INDEX, SPRITE_VISIBLE_INDEX, \
    PHYSICS_ACTIVE_INDEX, BEHAVIOR_ACTIVE_INDEX, AI_ACTIVE_INDEX, DEPENDENT_ENTITIES_INDEX, ETHEREAL_INDEX
from Sprite_state import SpriteStateEnum
from Game_Scene.Test.Test_Suites.test_Scene_functions import _spriteNetworkInActiveCellTest_

#(5.13) entity_id in _onscreen_entity_ids IFF self/dep/clone in active cell, or is AA
def _testOnscreenEntityIds_(game_engine_mock):
    try:
        entity_scene_manager = game_engine_mock._entity_scene_manager
        scene_manager = game_engine_mock._scene_manager
        active_entity_systems = entity_scene_manager._active_entity_systems
        active_scenes = scene_manager._active_scenes
        for scene_id, active_scene in active_scenes.items():
            __testOnscreenEntityIds__(active_scene, active_entity_systems[scene_id])
    except Exception as e:
        print(e)
        return False
    return True

#called by _testOnscreenEntityIds_ for each active scene
def __testOnscreenEntityIds__(scene, entity_manager):
    try:
        onscreen_entity_ids = entity_manager._onscreen_entity_ids
        sprites = scene._sprites
        for entity_id, sprite in sprites.items():
            if __spriteOnScreen__(sprite):
                if onscreen_entity_ids.get(entity_id) is None:
                    print("test_Entity_manager - onscreen sprite not in onscreen_entity_ids, id: ",entity_id)
                    assert False
            else:
                if onscreen_entity_ids.get(entity_id) is not None:
                    print("test_Entity_manager - offscreen sprite in onscreen_entity_ids, id: ", entity_id)
                    assert False
        for entity_id in onscreen_entity_ids.keys():
            if sprites.get(entity_id) is None:
                print("test_Entity_manager - entity_id in onscreen_entity_ids not in sprites, id: ", entity_id)
                assert False
    except Exception as e:
        print(e)
        assert False
    return True

#helper
#Returns True if sprite in active cell, in offscreen actives, has clone/dep in active cell, or is Always active
#else false
def __spriteOnScreen__(sprite):
    try:
        if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE:
            return True
        if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE:
            return True
        if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
            return True
        if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL:
            return True
        if _spriteNetworkInActiveCellTest_(sprite):
            return True
        return False
    except Exception as e:
        print(e)
        assert False

#(5.12) EntityManager references the correct scene
def _testEntityManagerCorrectScene_(game_engine_mock):
    try:
        entity_scene_manager = game_engine_mock._entity_scene_manager
        scene_manager = game_engine_mock._scene_manager
        scenes = scene_manager._scenes
        entity_systems = entity_scene_manager._entity_systems
        if entity_systems.keys() != scenes.keys():
            print("test_Entity_manager - scene handler key mismatch")
            assert False
        for scene_id, scene in scenes.items():
            if entity_systems[scene_id]._scene_handler != scene:
                print("test_Entity_manager - scene handler ref mismatch, id: " + str(scene_id))
                assert False
    except Exception as e:
        print(e)
        return False
    return True

#(5.1) Components active/inactive consistent with EM Status
#(5.2) Always_active entities active for all components
#(5.3) Not_Always_Active Components active iff onscreen, EM status
#(5.4) Deactivated entites inactive for all components
def _testActiveInactiveAcrossComponents_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._active_scene_ids:
            __testActiveInactiveAcrossComponents__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

def __testActiveInactiveAcrossComponents__(game_engine_mock, scene_id):
    #func pointer: <bool (entity_id)> - returns true if entity is within an active cell
    #spriteIsInActiveCell = game_engine_mock._scene_manager._scenes[scene_id].spriteIsInActiveCell
    entity_status_lists = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._entity_status_lists
    onscreen_entity_ids = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._onscreen_entity_ids
    active_physics_particles = game_engine_mock._physics_scene_manager._particle_component_systems[scene_id]._active_particles
    inactive_physics_particles = game_engine_mock._physics_scene_manager._particle_component_systems[scene_id]._inactive_particles
    active_behavior_components = game_engine_mock._behavior_scene_manager._behavior_component_systems[scene_id]._active_behaviorFSMs
    inactive_behavior_components = game_engine_mock._behavior_scene_manager._behavior_component_systems[scene_id]._inactive_behaviorFSMs
    active_ai_components = game_engine_mock._ai_scene_manager._ai_component_systems[scene_id]._active_ai_components
    inactive_ai_components = game_engine_mock._ai_scene_manager._ai_component_systems[scene_id]._inactive_ai_components
    sprites = game_engine_mock._scene_manager._scenes[scene_id]._sprites
    try:
        for entity_id, entity_status in entity_status_lists.items():
            if entity_status[ALWAYS_ACTIVE_INDEX]:
                if entity_status[ACTIVATED_INDEX]:
                    if onscreen_entity_ids.get(entity_id) is None:
                        print("test_Entity_manager - Activated, AA sprite not in onscreen_entity_ids, id: ", entity_id)
                        assert False
                else:
                    if onscreen_entity_ids.get(entity_id) is not None:
                        print("test_Entity_manager - DeActivated, AA sprite in onscreen_entity_ids, id: ", entity_id)
                        assert False
                #all components should be active, regardless of status
                if active_physics_particles.get(entity_id) is None:
                    print("test_Entity_manager - always active particle not in the active particle list, id: " + str(entity_id))
                    assert False
                if inactive_physics_particles.get(entity_id) is not None:
                    print("test_Entity_manager - always active particle in inactive particle list, id: " + str(entity_id))
                    assert False
                if active_ai_components.get(entity_id) is None:
                    print("test_Entity_manager - always active ai not in the active ai list, id: " + str(entity_id))
                    assert False
                if inactive_ai_components.get(entity_id) is not None:
                    print("test_Entity_manager - always active ai in inactive ai list, id: " + str(entity_id))
                    assert False
                if active_behavior_components.get(entity_id) is None:
                    print("test_Entity_manager - always active behavior not in the active behavior list, id: " + str(entity_id))
                    assert False
                if inactive_behavior_components.get(entity_id) is not None:
                    print("test_Entity_manager - always active behavior in inactive behavior list, id: " + str(entity_id))
                    assert False
            #components should be active if their status dictates, AND they are onscreen (or a dependant is)
            else:
                if entity_status[ACTIVATED_INDEX]:
                    #if _spriteOrDependantActive_(entity_id, entity_status[DEPENDENT_ENTITIES_INDEX],spriteIsInActiveCell):
                    if _spriteNetworkInActiveCellTest_(sprites[entity_id]):
                        if onscreen_entity_ids.get(entity_id) is None:
                            print("test_Entity_manager - Activated, sprite network in active cell not in onscreen_entity_ids, id: ",entity_id)
                            assert False
                    else:
                        if onscreen_entity_ids.get(entity_id) is not None:
                            print("test_Entity_manager - DeActivated, sprite network in onscreen_entity_ids, id: ",entity_id)
                            assert False
                if entity_status[PHYSICS_ACTIVE_INDEX]:
                    if active_physics_particles.get(entity_id) is None:
                        print("test_Entity_manager - active particle not in the active particle list, id: " + str(entity_id))
                        assert False
                    if inactive_physics_particles.get(entity_id) is not None:
                        print("test_Entity_manager - active particle in inactive particle list, id: " + str(entity_id))
                        assert False
                else: #physics inactive
                    if active_physics_particles.get(entity_id) is not None:
                        print("test_Entity_manager - inactive particle in the active particle list, id: " + str(entity_id))
                        assert False
                    if inactive_physics_particles.get(entity_id) is None:
                        print("test_Entity_manager - inactive particle not in inactive particle list, id: " + str(entity_id))
                        assert False
                if entity_status[BEHAVIOR_ACTIVE_INDEX]:
                    if active_behavior_components.get(entity_id) is None:
                        print("test_Entity_manager - test_Entity_manager - active behavior not in the active behavior list, id: " + str(entity_id))
                        assert False
                    if inactive_behavior_components.get(entity_id) is not None:
                        print("test_Entity_manager - test_Entity_manager - active behavior in inactive behavior list, id: " + str(entity_id))
                        assert False
                else:  # behavior inactive
                    if active_behavior_components.get(entity_id) is not None:
                        print("test_Entity_manager - inactive behavior in the active behavior list, id: " + str(entity_id))
                        assert False
                    if inactive_behavior_components.get(entity_id) is None:
                        print("test_Entity_manager - inactive behavior not in inactive behavior list, id: " + str(entity_id))
                        assert False
                if entity_status[AI_ACTIVE_INDEX]:
                    if active_ai_components.get(entity_id) is None:
                        print("test_Entity_manager - active ai not in the active ai list, id: " + str(entity_id))
                        assert False
                    if inactive_ai_components.get(entity_id) is not None:
                        print("test_Entity_manager - active ai in inactive ai list, id: " + str(entity_id))
                        assert False
                else:  # ai inactive
                    if active_ai_components.get(entity_id) is not None:
                        print("test_Entity_manager - inactive ai in the active ai list, id: " + str(entity_id))
                        assert False
                    if inactive_ai_components.get(entity_id) is None:
                        print("test_Entity_manager - inactive ai not in inactive ai list, id: " + str(entity_id))
                        assert False
        return True
    except Exception as e:
        print(e)
        assert False

#(5.5) Dependants have identical entity_stats
def _testEntityStatusIdenticalAcrossDependants_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._scene_ids:
            __testEntityStatusIdenticalAcrossDependants__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

def __testEntityStatusIdenticalAcrossDependants__(game_engine_mock, scene_id):
    try:
        entity_status_lists = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._entity_status_lists
        for entity_id, entity_status in entity_status_lists.items():
            em_dependants = entity_status[DEPENDENT_ENTITIES_INDEX]
            for dependant_entity_id in em_dependants:
                if not __entityStatusMatches__(entity_id, entity_status,
                                               dependant_entity_id, entity_status_lists[dependant_entity_id]):
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

#calls __testEntityDependanyConsistent__ for eachs cene
#(5.6) Dependants all have identical dependant lists
def _testEntityDependancyConsistent_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._scene_ids:
            __testEntityDependancyConsistent__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

#If entity A has entity B and C as a dependant, then entity B has A and C, and entity C has A and B
def __testEntityDependancyConsistent__(game_engine_mock, scene_id):
    try:
        entity_status_lists = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._entity_status_lists
        for entity_id, entity_status in entity_status_lists.items():
            em_dependants = entity_status[DEPENDENT_ENTITIES_INDEX]
            count = len(em_dependants)
            index = 0
            while index < count:
                entity_test_id = em_dependants[index]
                entity_test_status = entity_status_lists[entity_test_id]
                for entity_test_status_dependant_id in entity_test_status[DEPENDENT_ENTITIES_INDEX]:
                    if not entity_test_status_dependant_id in em_dependants:
                        if entity_test_status_dependant_id != entity_id:
                            print("test_Entity_manager - expected to see id " + str(entity_test_status_dependant_id)+
                                  " as dependant of " + str(entity_test_id))
                            assert False
                index+=1
    except Exception as e:
        print(e)
        assert False
    return True

# calls __testEntityStatusSpriteDependantEqual__ for all scenes
def _testEntityStatusSpriteDependantEqual_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._scene_ids:
            __testEntityStatusSpriteDependantEqual__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

#(5.7) Active sprites do not have nodes in the deactivated_dependants
#(5.8) Deactivated sprites don't have nodes in dependant_sprite_nodes
#(5.9) Only active nodes in dependant_sprite_nodes
#(5.10) Only deactivated or AAinvisible nodes in inactive_dependants
#(5.11) Sprite and EM Status dependants list are identical
#verifies sprite in scene handler and status in EM share the same entity dependants list
def __testEntityStatusSpriteDependantEqual__(game_engine_mock, scene_id):
    try:
        entity_status_lists = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._entity_status_lists
        sprites = game_engine_mock._scene_manager._scenes[scene_id]._sprites
        for entity_id, entity_status in entity_status_lists.items():
            if sprites.get(entity_id) is None:
                print("test_Entity_manager - entity_id in Entity manager not in scene_layer, id: " + str(entity_id))
                assert False
            #need these 2 lists to be identical
            sprite = sprites[entity_id]
            em_dependants = entity_status[DEPENDENT_ENTITIES_INDEX]
            if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                dependant_list = sprite.inactive_dependants
                if len(sprite.dependant_sprite_nodes) > 0: #89
                    print("test_Entity_manager - AAinvisible sprite has nodes in active_dependants, id: "+ str(entity_id))
                    assert False
                for dep_sprite in dependant_list.values(): #87
                    if not dep_sprite.isActivated():
                        print("test_Entity_manager - AAinvisible sprite is inactive inactive_dependants, id: "+ str(entity_id))
                        assert False
            elif sprite.isActivated():
                dependant_list = sprite.dependant_sprite_nodes
                if len(sprite.inactive_dependants) > 0: #88
                    print("test_Entity_manager - active sprite has nodes in inactive_dependants, id: "+ str(entity_id))
                    assert False
                for dep_sprite in dependant_list.values(): #86
                    if not dep_sprite.isActivated():
                        print("test_Entity_manager - deactivated sprite in dependant_sprite_nodes, id: "+ str(entity_id))
                        assert False
            ##Deactivated
            else:
                dependant_list = sprite.inactive_dependants
                if len(sprite.dependant_sprite_nodes) > 0: #89
                    print("test_Entity_manager - inactive sprite has nodes in active_dependants, id: "+ str(entity_id))
                    assert False
                for dep_sprite in dependant_list.values(): #87
                    if dep_sprite.isActivated():
                        print("test_Entity_manager - activated sprite in inactive_dependants, id: "+ str(entity_id))
                        assert False
            for dependant_entity_id in dependant_list.keys():
                if dependant_entity_id not in em_dependants:
                    print("test_Entity_manager - Id " + str(dependant_entity_id) + " in sprite list not in em, id: " + str(entity_id))
                    assert False
            for dependant_entity_id in em_dependants:
                if dependant_list.get(dependant_entity_id) is None:
                    print("test_Entity_manager - Id " + str(dependant_entity_id) + "in EM list not in sprite, id: " + str(entity_id))
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(5.14) All EM Entity_Ids are in Scene Layer
#(5.15) All Scene_Layer Entities are in EM
#(5.16) Sprite States are consistent with Entity Status
def _testSpriteStateEntityStatusMatch_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._scene_ids:
            __testSpriteStateEntityStatusMatch__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

def __testSpriteStateEntityStatusMatch__(game_engine_mock, scene_id):
    try:
        entity_status_lists = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._entity_status_lists
        sprites = game_engine_mock._scene_manager._scenes[scene_id]._sprites
        #check all entities in EM
        for entity_id, entity_status in entity_status_lists.items():
            if sprites.get(entity_id) is None:
                print("test_Entity_manager - active entity_id in Entity manager not in scene_layer, id: " + str(entity_id))
                assert False
            sprite = sprites[entity_id]
            sprite_state_enum = sprite.getSpriteStateEnum()
            #Create a tuple with the relavent staus Bools, which maps to the expected state
            status_mapping = (entity_status[ACTIVATED_INDEX],
                              entity_status[ETHEREAL_INDEX],
                              entity_status[ALWAYS_ACTIVE_INDEX],
                              entity_status[SPRITE_VISIBLE_INDEX])
            expected_state_enum = _SPRITE_STATE_MAP_[status_mapping] #[active, ethereal, always_active, visible]
            if sprite_state_enum != expected_state_enum:
                print("test_Entity_manager - Expected sprite state: " + str(expected_state_enum))
                print("got sprite state: " + str(sprite_state_enum) + " , entity id: " + str(entity_id))
                assert False
        # (5.15) All Scene_Layer Entities are in EM
        for entity_id, entity_status in sprites.items():
            if entity_status_lists.get(entity_id) is None:
                print("test_Entity_manager - active entity_id in scene layer not in scene_layer, id: " + str(entity_id))
                assert False
    except Exception as e:
        print(e)
        assert False
    return True

### Helper Functions ###

#returns true if the entity status are matching
def __entityStatusMatches__(entity_id_1, entity_status_1, entity_id_2, entity_status_2):
    try:
        #check the boolean flags
        if entity_status_1[ACTIVATED_INDEX] == entity_status_2[ACTIVATED_INDEX] and \
               entity_status_1[ALWAYS_ACTIVE_INDEX] == entity_status_2[ALWAYS_ACTIVE_INDEX] and \
               entity_status_1[SPRITE_VISIBLE_INDEX] == entity_status_2[SPRITE_VISIBLE_INDEX] and \
               entity_status_1[ETHEREAL_INDEX] == entity_status_2[ETHEREAL_INDEX] and \
               entity_status_1[PHYSICS_ACTIVE_INDEX] == entity_status_2[PHYSICS_ACTIVE_INDEX] and \
               entity_status_1[BEHAVIOR_ACTIVE_INDEX] == entity_status_2[BEHAVIOR_ACTIVE_INDEX] and \
               entity_status_1[AI_ACTIVE_INDEX] == entity_status_2[AI_ACTIVE_INDEX]:
            #compare the dependant entity id lists (order does not matter)
            for dependant_entity_id in entity_status_1[DEPENDENT_ENTITIES_INDEX]:
                #the only difference between the lists is that an entity won't have it's own id in the list
                if dependant_entity_id not in entity_status_2[DEPENDENT_ENTITIES_INDEX] and \
                    dependant_entity_id != entity_id_2:
                    print("test_Entity_manager - entity_id " + str(entity_id_1) + " has dependant id " + str(dependant_entity_id))
                    print("entity_id " + str(entity_id_2) + " does not")
                    assert False
            for dependant_entity_id in entity_status_2[DEPENDENT_ENTITIES_INDEX]:
                #the only difference between the lists is that an entity won't have it's own id in the list
                if dependant_entity_id not in entity_status_1[DEPENDENT_ENTITIES_INDEX] and \
                    dependant_entity_id != entity_id_1:
                    print("test_Entity_manager - entity_id " + str(entity_id_2) + " has dependant id " + str(dependant_entity_id))
                    print("entity_id " + str(entity_id_1) + " does not")
                    assert False
        else:
            print("test_Entity_manager - entity id " + str(entity_id_1) + " and entity id " + str(entity_id_2) + " status mismatch")
            assert False
    except Exception as e:
        print(e)
        return False
    return True

_SPRITE_STATE_MAP_ = dict()  # {[active, ethereal, always_active, visible] : SpriteState}
_SPRITE_STATE_MAP_[True, True, True, True] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL
_SPRITE_STATE_MAP_[True, True, True, False] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL
_SPRITE_STATE_MAP_[True, True, False, True] = SpriteStateEnum.SPRITE_STATE_ACTIVE_ETHEREAL
_SPRITE_STATE_MAP_[True, True, False, False] = SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL

_SPRITE_STATE_MAP_[True, False, True, True] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE
_SPRITE_STATE_MAP_[True, False, True, False] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE
_SPRITE_STATE_MAP_[True, False, False, True] = SpriteStateEnum.SPRITE_STATE_ACTIVE
_SPRITE_STATE_MAP_[True, False, False, False] = SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE

_SPRITE_STATE_MAP_[False, True, True, True] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED
_SPRITE_STATE_MAP_[False, True, True, False] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED
_SPRITE_STATE_MAP_[False, True, False, True] = SpriteStateEnum.SPRITE_STATE_ETHEREAL_DEACTIVATED
_SPRITE_STATE_MAP_[False, True, False, False] = SpriteStateEnum.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED

_SPRITE_STATE_MAP_[False, False, True, True] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED
_SPRITE_STATE_MAP_[False, False, True, False] = SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED
_SPRITE_STATE_MAP_[False, False, False, True] = SpriteStateEnum.SPRITE_STATE_DEACTIVATED
_SPRITE_STATE_MAP_[False, False, False, False] = SpriteStateEnum.SPRITE_STATE_INVISIBLE_DEACTIVATED




