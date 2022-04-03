from Sprite_state import SpriteStateEnum

#(1.8) scene_layer references the correct scene
#(1.9) all scene_layers reference same master grid
#(1.10) scene_grid is unique to scene_layer
#(1.11) each master_grid unique to each scene
#(1.12) all scene_layers unique to scene
#(1.13) each scene_grids scene_layer reference is correct
#(1.14) each scene_grids master_grid reference is correct
#(1.15) master_grid has 1 scene_grid per layer, references are consistent
#(1.16) in scene_manager all scenes refs are unique instances
#(1.17) master_grid scene reference is correct
#(1.18) Scene.scene_id value matches dict
#(1.19) Layer.layer_id value matches scene dict
def _testSceneLayerReferences_(game_engine_mock):
    try:
        #store the references to ensure no duplicates
        master_grid_refs = list()
        scene_layer_refs = list()
        scene_grid_refs = list()
        scene_refs = list()
        scene_manager = game_engine_mock._scene_manager
        for scene_id, scene in scene_manager._scenes.items():
            scene.scene_id = scene_id
            if scene in scene_refs:
                print("test_Scene_layer - duplicate scene reference id: " + str(scene_id))
                assert False
            scene_refs.append(scene)
            master_grid = scene._scene_master_grid
            if master_grid in master_grid_refs:
                print("test_Scene_layer - duplicate master grid reference id: " + str(scene_id))
                assert False
            master_grid_refs.append(master_grid)
            if master_grid.scene != scene:
                print("test_Scene_layer - master grid reference wrong scene, id: " + str(scene_id))
                assert False
            numb_scene_layers = len(scene._scene_layers)
            if len(master_grid._scene_grids) != numb_scene_layers:
                print("test_Scene_layer - numb layers and numb grids mismatch: " + str(scene_id))
                assert False
            for scene_grid in master_grid._scene_grids.values():
                if scene_grid.master_grid != master_grid:
                    print("test_Scene_layer - mastergrid ref mismatch: " + str(scene_id))
                    assert False
            if master_grid._scene_grids.keys() != scene._scene_layers.keys():
                print("test_Scene_layer - mastergrid and scene should have same layer keys: " + str(scene_id))
                assert False
            for layer_id, scene_layer in scene._scene_layers.items():
                scene_layer.layer_id = layer_id
                if scene_layer in scene_layer_refs:
                    print("test_Scene_layer - duplicate layer reference id: " + str(scene_id))
                    assert False
                scene_layer_refs.append(scene_layer)
                if scene_layer.scene != scene:
                    print("test_Scene_layer - layer scene ref mismatch: " + str(scene_id))
                    assert False
                if scene_layer.master_grid != master_grid:
                    print("test_Scene_layer - layer master grid ref mismatch: " + str(scene_id))
                    assert False
                scene_grid = scene_layer.scene_grid
                if scene_grid.scene_layer != scene_layer:
                    print("test_Scene_layer - scene grid layer ref mismatch: " + str(scene_id))
                    assert False
                if scene_grid in scene_grid_refs:
                    print("test_Scene_layer - duplicate scene_grid: " + str(scene_id))
                    assert False
                scene_grid_refs.append(scene_grid)
    except Exception as e:
        print(e)
        return False
    return True

#calls __testEntityIdVerification__ for each scene
def _testEntityReferences_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._scene_ids:
            __testEntityReferences__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

#(1.1) All activated Entity_IDs in Scene_Layer are in Grid
    #unless AAInvisibleEthereal, those are in their own list in the scene, not in the grid
    #Active Invisibles Ethereals are in a dict, not a LL, in a cell
#(1.2) No Duplicate Sprite References in Grid
#(1.3) Entity_Id returns same sprite in Scene_Layer and Grid
#(1.4) No Duplicate Sprite References in Scene_Layer
#(1.5) No inactive sprites are in Grid
def __testEntityReferences__(game_engine_mock, scene_id):
    try:
        sprites_dict = game_engine_mock._scene_manager._scenes[scene_id]._sprites
        sprite_list = list()
        for entity_id, sprite in sprites_dict.items():
            is_activated = sprite.isActivated()
            is_visible = sprite.isVisible()
            is_ethereal = sprite.isEthereal()
            #We will check all 3 possible locations for the ID, then verify it is where it is supposed to be
            linked_list_sprite = __findVisibleSpriteIdInLinkedList__(sprite.grid, entity_id)
            invisible_tangible_node = __findVisibleSpriteIdInInvTangible__(sprite.grid, entity_id)
            invisible_ethereal_node = __findVisibleSpriteIdInInvEthereal__(sprite.grid, entity_id)
            if sprite.current_sprite_state.sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                if linked_list_sprite is not None or linked_list_sprite is False:
                    print("test_Scene_layer - AAInvisibleEthereal was in the cell, id: " + str(entity_id))
                    assert False
                if invisible_tangible_node is not None or invisible_tangible_node is False:
                    print("test_Scene_layer - AAInvisibleEthereal was in the cell, id: " + str(entity_id))
                    assert False
                if invisible_ethereal_node is not None or invisible_ethereal_node is False:
                    print("test_Scene_layer - AAInvisibleEthereal was in the cell, id: " + str(entity_id))
                    assert False
            #visible sprites are in the linked list
            elif is_activated and is_visible:
                if linked_list_sprite is None:
                        print("test_Scene_layer - ID in dict does not return a sprite in the grid, id: " + str(entity_id))
                        assert False
                if invisible_tangible_node is not None or invisible_tangible_node is False:
                    print("test_Scene_layer - unexpected invisible_tangible_node found, id: " + str(entity_id))
                    assert False
                if invisible_ethereal_node is not None or invisible_ethereal_node is False:
                    print("test_Scene_layer - unexpected invisible_ethereal_node was found, id: " + str(entity_id))
                    assert False
                if not linked_list_sprite:
                    print("test_Scene_layer - duplicate sprite reference for id")
                    assert False
                if linked_list_sprite != sprite:
                    print("test_Scene_layer - ID in dict does not return the same sprite object in grid, id: " + str(entity_id))
                    assert False
                if linked_list_sprite in sprite_list:
                    print('test_Scene_layer - Duplicate sprite in dict, id: ' + str(entity_id))
                    assert False
                sprite_list.append(linked_list_sprite)
            #invisible ethereal sprites are
            elif is_activated and (not is_visible and is_ethereal):
                if linked_list_sprite is not None:
                    print("test_Scene_layer - invisible ethereal sprite found in cell LL, id: " + str(entity_id))
                    assert False
                if invisible_tangible_node is not None or invisible_tangible_node is False:
                    print("test_Scene_layer - unexpected invisible_tangible_node was found, id: " + str(entity_id))
                    assert False
                if invisible_ethereal_node is None:
                    print("test_Scene_layer - invisible_ethereal_node was in the LL, id: " + str(entity_id))
                    assert False
                if not invisible_ethereal_node:
                    print("test_Scene_layer - duplicate sprite reference for id")
                    assert False
                if invisible_ethereal_node != sprite:
                    print("test_Scene_layer - ID in dict does not return the same sprite object in grid, id: " + str(entity_id))
                    assert False
                if invisible_ethereal_node in sprite_list:
                    print('test_Scene_layer - Duplicate sprite in dict, id: ' + str(entity_id))
                    assert False
                sprite_list.append(invisible_ethereal_node)
            elif is_activated and (not is_visible and not is_ethereal):
                if linked_list_sprite is not None:
                    print("test_Scene_layer - invisible tangible sprite found in cell LL, id: " + str(entity_id))
                    assert False
                if invisible_ethereal_node is not None or invisible_ethereal_node is False:
                    print("test_Scene_layer - unexpected invisible_ethereal_node was found, id: " + str(entity_id))
                    assert False
                if invisible_tangible_node is None or invisible_tangible_node is False:
                    print("test_Scene_layer - invisible_tangible_node was in the LL, id: " + str(entity_id))
                    assert False
                if not invisible_tangible_node:
                    print("test_Scene_layer - duplicate sprite reference for id")
                    assert False
                if invisible_tangible_node != sprite:
                    print("test_Scene_layer - ID in dict does not return the same sprite object in grid, id: " + str(entity_id))
                    assert False
                if invisible_tangible_node in sprite_list:
                    print('test_Scene_layer - Duplicate sprite in dict, id: ' + str(entity_id))
                    assert False
                sprite_list.append(invisible_tangible_node)
            elif not is_activated:
                if linked_list_sprite is not None or linked_list_sprite is False:
                    print("test_Scene_layer - deactivated sprite found in grid, id: " + str(entity_id))
                    assert False
                if invisible_tangible_node is not None or invisible_tangible_node is False:
                    print("test_Scene_layer - unexpected invisible_tangible_node found, id: " + str(entity_id))
                    assert False
                if invisible_ethereal_node is not None or invisible_ethereal_node is False:
                    print("test_Scene_layer - unexpected invisible_ethereal_node was found, id: " + str(entity_id))
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

#returns True if the id is found in one of the grid layers, else false
# Returns the sprite with the id
# Returns None if not found
# Verifies that there is only one reference to the sprite with this id
# Asserts an error if there is a duplicate
def __findVisibleSpriteIdInLinkedList__(scene_grid, entity_id):
    try:
        sprite_found = None
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                retVal = __findSpriteIdInCellLinkedList__(cell, entity_id)
                if retVal is not None:
                    if not retVal:
                        return False
                    if sprite_found is not None:
                        print("DynamicGrid.__findSpriteId__() duplicate sprite reference for id: " + str(entity_id))
                        return False
                    else:
                        sprite_found = retVal
    except Exception as e:
        print(e)
        return False
    return sprite_found

#Returns the sprite with the matching id
    #if not found returns none
#checks for duplicate, asserts an error if more than 1 sprite with id found
def __findSpriteIdInCellLinkedList__(cell, entity_id):
    try:
        if cell.head is None:
            return None
        sprite_found = None
        current = cell.head
        while current is not None:
            #We will come up with duplicate id's (as we should) if we check clones AND Instances
            if current.__class__.__name__ == "SpriteNode" and current.getEntityId() == entity_id:
                if sprite_found is not None:
                    print("Duplicate sprite reference in cell " + str(cell.cell_id) + " with sprite id: " + str(entity_id))
                    return False
                else:
                    sprite_found = current
            current = current.next_node
    except Exception as e:
        print(e)
        return False
    return sprite_found

#like __findVisibleSpriteIdInLinkedList__ but for invisible_ethereal_nodes
def __findVisibleSpriteIdInInvEthereal__(scene_grid, entity_id):
    try:
        sprite_found = None
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                retVal = __findSpriteIdInCellInvEthereal__(cell, entity_id)
                if retVal is not None:
                    if not retVal:
                        return False
                    if sprite_found is not None:
                        print("DynamicGrid.__findSpriteId__() duplicate sprite reference for id: " + str(entity_id))
                        return False
                    else:
                        sprite_found = retVal
    except Exception as e:
        print(e)
        return False
    return sprite_found

def __findSpriteIdInCellInvEthereal__(cell, entity_id):
    try:
        sprite_found = None
        for node in cell.invisible_ethereal_nodes.values():
            #We will come up with duplicate id's (as we should) if we check clones AND Instances
            if node.__class__.__name__ == "SpriteNode" and node.getEntityId() == entity_id:
                if sprite_found is not None:
                    print("Duplicate sprite reference in cell " + str(cell.cell_id) + " with sprite id: " + str(entity_id))
                    return False
                else:
                    sprite_found = node
    except Exception as e:
        print(e)
        return False
    return sprite_found

#like __findVisibleSpriteIdInLinkedList__ but for invisible nodes
def __findVisibleSpriteIdInInvTangible__(scene_grid, entity_id):
    try:
        sprite_found = None
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                retVal = __findSpriteIdInCellInvTangible__(cell, entity_id)
                if retVal is not None:
                    if not retVal:
                        return False
                    if sprite_found is not None:
                        print("DynamicGrid.__findSpriteId__() duplicate sprite reference for id: " + str(entity_id))
                        return False
                    else:
                        sprite_found = retVal
    except Exception as e:
        print(e)
        return False
    return sprite_found

def __findSpriteIdInCellInvTangible__(cell, entity_id):
    try:
        sprite_found = None
        current_node = cell.invisible_head
        while current_node is not None:
            #We will come up with duplicate id's (as we should) if we check clones AND Instances
            if current_node.__class__.__name__ == "SpriteNode" and current_node.getEntityId() == entity_id:
                if sprite_found is not None:
                    print("Duplicate sprite reference in cell " + str(cell.cell_id) + " with sprite id: " + str(entity_id))
                    return False
                else:
                    sprite_found = current_node
            current_node = current_node.next_node
    except Exception as e:
        print(e)
        return False
    return sprite_found

#'active' here just means still existing, they can be deactivated
#(1.6) All expected entity_ids in Scene Layer
#(1.7) No unexpected entity_ids in Scene Layer
def _testVerifyActiveEntities_(game_engine_mock):
    try:
        testing_system_entity_ids = game_engine_mock.getAllTestingEntityIds()
        for entity_id in testing_system_entity_ids: #(5)
            test_id_found = False
            for scene in game_engine_mock._scene_manager._scenes.values():
                if scene._sprites.get(entity_id) is not None:
                    if test_id_found:
                        print("test_Scene_layer - duplicate entity id found, id: " + str(entity_id))
                        assert False
                    else:
                        test_id_found = True
            if not test_id_found:
                print("test_Scene_layer - Expected entity id is missing, id: " + str(entity_id))
                assert False
        for scene in game_engine_mock._scene_manager._scenes.values(): #(6)
            for sprite_id in scene._sprites.keys():
                if sprite_id not in testing_system_entity_ids:
                    print("test_Scene_layer - Unexpected entity_id found, id: " + str(sprite_id))
                    assert False
    except Exception as e:
        print(e)
        return False
    return True

#(1.20) entity_id_by_layer contains same entity_ids list as main sprite list
def _testEntityByLayerId_(game_engine_mock):
    try:
        scene_manager = game_engine_mock._scene_manager
        for scene_id, scene in scene_manager._scenes.items():
            entity_id_by_layer = scene._entity_id_by_layer
            sprites = scene._sprites
            for entity_id in entity_id_by_layer.keys():
                if sprites.get(entity_id) is None:
                    print("test_Scene_layer Entity id in entity_id_by_layer but not in Sprites")
                    print(scene_id, entity_id)
                    assert False
            for entity_id in sprites.keys():
                if entity_id_by_layer.get(entity_id) is None:
                    print("test_Scene_layer Entity id in sprites but not in entity_id_by_layer")
                    print(scene_id, entity_id)
                    assert False
    except Exception as e:
        print(e)
        return False
    return True

#(1.21) _testing_layer_ids matches actual layer lists
def _testCurrentLayerIds_(game_engine_mock):
    try:
        testing_layer_ids = game_engine_mock._testing_layer_ids
        scenes = game_engine_mock._scene_manager._scenes
        for scene_id, scene in scenes.items():
            if testing_layer_ids.get(scene_id) is None:
                print("test_Scene_layer missing scene id in testing_layer_ids, ",scene_id)
                assert False
            current_testing_layer_ids = testing_layer_ids.get(scene_id)
            for layer_id in scene._scene_layers.keys():
                if layer_id not in current_testing_layer_ids:
                    print("test_Scene_layer missing layer id in testing_active_layer_ids, ", scene_id, layer_id)
                    assert False
        for testing_scene_id, testing_layer_ids in testing_layer_ids.items():
            if scenes.get(testing_scene_id) is None:
                print("test_Scene_layer scene id in testing list not in manager list, ", testing_scene_id)
                assert False
            for testing_layer_id in testing_layer_ids:
                if scenes[testing_scene_id]._scene_layers.get(testing_layer_id) is None:
                    print("test_Scene_layer layer id in testing list not in manager list, ", testing_scene_id, testing_layer_id)
                    assert False
    except Exception as e:
        print(e)
        return False
    return True
