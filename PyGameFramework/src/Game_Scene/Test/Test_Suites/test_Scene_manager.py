
#(6.8) cell_size is less than or equal to world_size
#(6.9) activation_range is less than deactivation_range
#(6.10) tile_size is less than or equal to cell_size
#(6.11) tile_size is a multiple of cell_size
def _testSceneSizeParameters_(game_engine_mock):
    try:
        scenes = game_engine_mock._scene_manager._scenes
        for scene_id, scene in  scenes.items():
            #(6.8)
            if scene.cell_size[0] >  scene.world_size[0]:
                print("test_Scene_manager - cell size x > world size x, id: ",scene_id)
                assert False
            if scene.cell_size[1] >  scene.world_size[1]:
                print("test_Scene_manager - cell size y > world size y, id: ",scene_id)
                assert False
            #(6.10)
            if scene.tile_size[0] >  scene.cell_size[0]:
                print("test_Scene_manager - tile size x > cell size x, id: ",scene_id)
                assert False
            if scene.tile_size[1] >  scene.cell_size[1]:
                print("test_Scene_manager - tile size y > cell size y, id: ",scene_id)
                assert False
            #(6.11)
            if scene.cell_size[0] % scene.tile_size[0] !=0:
                print("test_Scene_manager - tile size x not multiple of cell size, id:",scene_id)
                assert False
            if scene.cell_size[1] % scene.tile_size[1] !=0:
                print("test_Scene_manager - tile size y not multiple of cell size, id:",scene_id)
                assert False
        cameras = game_engine_mock._camera_manager._cameras
        for camera_id, camera in cameras.items():
            #(6.9)
            if camera.activate_range[0] >= camera.deactivate_range[0]:
                print("test_Scene_manager - activate range x > deactivate range x id:",camera_id)
                assert False
            if camera.activate_range[1] >= camera.deactivate_range[1]:
                print("test_Scene_manager - activate range y > deactivate range y id:",camera_id)
                assert False
    except Exception as e:
        print(e)
        return False
    return True

#(6.7) _entity_scene_map dicts accurate and consistent
def _testEntitySceneMap_(game_engine_mock):
    try:
        entity_status_scene_manager = game_engine_mock._entity_scene_manager
        entity_scene_map = entity_status_scene_manager._entity_scene_map
        testing_system_entity_ids = game_engine_mock.testing_system_entity_ids
        for scene_id, entity_ids in testing_system_entity_ids.items():
            for entity_id in entity_ids:
                if entity_scene_map[entity_id][0] != scene_id:
                    print("test_Scene_manager - testing_system_entity_ids scene_id mismatch")
                    assert False
        for entity_id, scene_layer_pair in entity_scene_map.items():
            #Verify that the scene_id exists in the game engine list
            if testing_system_entity_ids.get(scene_layer_pair[0]) is None:
                print("test_Scene_manager - entity_scene_map contains scene_id not in game engine testing_system_entity_ids")
                assert False
            #Verify game engine and entity manager agree about the scene_id/entity_id pairing
            if not entity_id in testing_system_entity_ids[scene_layer_pair[0]]:
                print("test_Scene_manager - entity_scene_map entity_id mismatch game engine testing_system_entity_ids")
                assert False
    except Exception as e:
        print(e)
        return False
    return True

#(6.5) scene_ids for each component of entity consistent
#(6.6) game engines test scenes ids list match scene manager
def _testEntityInCorrectSceneManagers_(game_engine_mock):
    try:
        physics_scenes = game_engine_mock._physics_scene_manager._particle_component_systems
        behavior_scenes = game_engine_mock._behavior_scene_manager._behavior_component_systems
        ai_scenes = game_engine_mock._ai_scene_manager._ai_component_systems
        entity_systems = game_engine_mock._entity_scene_manager._entity_systems
        game_enging_scene_ids = game_engine_mock._scene_ids
        game_enging_active_scene_ids = game_engine_mock._active_scene_ids
        #(6.6)
        if not game_enging_scene_ids.sort() == list(game_engine_mock._scene_manager._scenes.keys()).sort():
            print("test_Scene_manager - game engine test list of scene ids mismatch")
            assert False
        if not game_enging_active_scene_ids.sort() == list(game_engine_mock._scene_manager._active_scenes.keys()).sort():
            print("test_Scene_manager - game engine test list of active scene ids mismatch")
            assert False
        for scene_id, scene in game_engine_mock._scene_manager._scenes.items():
            for entity_id, sprite in scene._sprites.items():
                #PHYSICS
                try:
                    particle = physics_scenes[scene_id]._active_particles[entity_id]
                except:
                    particle = physics_scenes[scene_id]._inactive_particles.get(entity_id)
                #Ensure we have a matching reference, not just value
                if particle is None or not (particle._position is sprite.ground_position):
                    print("test_Scene_manager - sprite particle ref mismatch: " + str(scene_id))
                    assert False
                #BEHAVIOR
                try:
                    behaviorFSM = behavior_scenes[scene_id]._active_behaviorFSMs[entity_id]
                except:
                    behaviorFSM = behavior_scenes[scene_id]._inactive_behaviorFSMs.get(entity_id)
                #Ensure we have a matching reference, not just value
                if behaviorFSM is None or \
                        not (sprite.state_has_changed is behaviorFSM.state_has_changed) or \
                        not (sprite.animation_has_flipped is behaviorFSM.animation_has_flipped):
                    print("test_Scene_manager - sprite behavior ref mismatch: " + str(scene_id))
                    assert False
                #AI
                try:
                    ai_component = ai_scenes[scene_id]._active_ai_components[entity_id]
                except:
                    ai_component = ai_scenes[scene_id]._inactive_ai_components.get(entity_id)
                #There is no interesting 'stuff' in ai to compare just yet
                if ai_component is None:
                    print("test_Scene_manager - sprite ai ref mismatch: " + str(scene_id))
                    assert False
                #EM
                entity_status = entity_systems[scene_id]._entity_status_lists.get(entity_id)
                if entity_status is None:
                    print("test_Scene_manager - sprite entity status ref mismatch: " + str(scene_id))
                    assert False
    except Exception as e:
        print(e)
        return False
    return True

#(6.1) All scenes in active_scenes list in _scenes list
#(6.2) Each manager has 1 component system per scene with matching ID
#(6.3) All managers have same scenes
#(6.4) All managers have same active scenes
def _testSceneReferencesMatch_(game_engine_mock):
    try:
        scene_manager = game_engine_mock._scene_manager
        scenes = scene_manager._scenes
        active_scenes = scene_manager._active_scenes
        for scene_id, active_scene in active_scenes.items():
            if scenes[scene_id] != active_scene: #(6.1)
                print("test_Scene_manager - active scene ref mismatch: " + str(scene_id))
                assert False
        physics_scene_manager = game_engine_mock._physics_scene_manager
        particle_component_systems = physics_scene_manager._particle_component_systems
        active_particle_systems = physics_scene_manager._active_component_systems
        for scene_id, active_scene in active_particle_systems.items():
            if particle_component_systems[scene_id] != active_scene: #(6.1)
                print("test_Scene_manager - active particle scene ref mismatch: " + str(scene_id))
                assert False
        behavior_scene_manager = game_engine_mock._behavior_scene_manager
        behavior_component_systems = behavior_scene_manager._behavior_component_systems
        behavior_active_systems = behavior_scene_manager._active_component_systems
        for scene_id, active_scene in behavior_active_systems.items():
            if behavior_component_systems[scene_id] != active_scene: #(6.1)
                print("test_Scene_manager - active behavior scene ref mismatch: " + str(scene_id))
                assert False
        ai_scene_manager = game_engine_mock._ai_scene_manager
        ai_component_systems = ai_scene_manager._ai_component_systems
        active_ai_systems = ai_scene_manager._active_component_systems
        for scene_id, active_scene in active_ai_systems.items():
            if ai_component_systems[scene_id] != active_scene: #(6.1)
                print("test_Scene_manager - active ai scene ref mismatch: " + str(scene_id))
                assert False
        #there isn't a distinction with entity manager active keys because entity managers don't update loop
        entity_scene_manager = game_engine_mock._entity_scene_manager
        entity_systems = entity_scene_manager._entity_systems
        #(6.3)
        if not (scenes.keys()
                == particle_component_systems.keys()
                == behavior_component_systems.keys()
                == ai_component_systems.keys()
                == entity_systems.keys()):
            print("test_Scene_manager - scene key mismatch")
            assert False
        #(6.4)
        if not (active_scenes.keys()
                == active_particle_systems.keys()
                == behavior_active_systems.keys()
                == active_ai_systems.keys()):
            print("test_Scene_manager - scene key mismatch")
            assert False
    except Exception as e:
        print(e)
        return False
    return True