from Game_Scene.Scene_Cell.Scene_cell import CellStateEnum
from Sprite_state import SpriteStateEnum
from Game_Scene.Test.Test_Suites.test_Scene_functions import _ceiling_, _getNodeByEntityIdInCell_, \
    _isCloneBased_, _isHorizontalCloneBased_, _spriteNetworkInActiveCellTest_

#(4.10) particle reference is correct, particle reference in 1 and only 1 node
#(4.11) behavior reference is correct, behavior reference in 1 and only 1 node
def _testSpriteComponentReferences_(game_engine_mock):
    try:
        particles = list()
        behaviorFSMs = list()
        for scene_id, scene in game_engine_mock._scene_manager._scenes.items():
            for entity_id, sprite in scene._sprites.items():
                particle = sprite.particle
                if particle.entity_id != entity_id:
                    print("test_Scene_node - particle id mismatch: " + str(entity_id))
                    assert False
                if particle in particles:
                    print("test_Scene_node - duplicate particle: " + str(entity_id))
                    assert False
                particles.append(particle)
                behaviorFSM = sprite.behaviorFSM
                if behaviorFSM.entity_id != entity_id:
                    print("test_Scene_node - behaviorFSM id mismatch: " + str(entity_id))
                    assert False
                if behaviorFSM in behaviorFSMs:
                    print("test_Scene_node - duplicate behaviorFSM: " + str(entity_id))
                    assert False
                behaviorFSMs.append(behaviorFSM)
    except Exception as e:
        print(e)
        return False
    return True

#(4.20) Clones are in the same layer as the sprite
#(4.21) Sprites are a part of a scene which is part of scene manager (not floating)
#(4.22) Node layer ref mayches cell layer ref
#(4.23) All Sprites dependants part of same scene_layer
def _testDependantsInSameLayer_(game_engine_mock):
    try:
        for scene_id, scene in game_engine_mock._scene_manager._scenes.items():
            for entity_id, sprite in scene._sprites.items():
                if sprite.isActivated() and not (sprite.isAlwaysActive() and not sprite.isVisible()):
                    if sprite.cell.scene_layer.scene != scene: #(4.21) - kind of.  The objective is a little dumb
                        print("test_Scene_node - scene ref mismatch: " + str(entity_id))
                        assert False
                    scene_layer = sprite.cell.scene_layer
                    if not sprite.layer is scene_layer:
                        print("test_Scene_node - layer ref mismatch: " + str(entity_id))
                        assert False
                    for dependant in sprite.dependant_sprite_nodes.values():
                        if dependant.cell.scene_layer != scene_layer: #(4.23)
                            print("test_Scene_node - scene layer dep mismatch: " + str(entity_id))
                            assert False
                    #(4.20)
                    if sprite.horizontal_clone is not None:
                        __recursiveHCloneLayerCheck__(entity_id, scene_layer, sprite.horizontal_clone)
                    if sprite.vertical_clone is not None:
                        __recursiveVCloneLayerCheck__(entity_id, scene_layer, sprite.vertical_clone)
    except Exception as e:
        print(e)
        return False
    return True

def __recursiveHCloneLayerCheck__(entity_id, scene_layer, clone):
    try:
        if clone.cell.scene_layer != scene_layer:
            print("test_Scene_node - scene layer hclone mismatch: " + str(entity_id))
            assert False
        if clone.horizontal_clone is not None:
            __recursiveHCloneLayerCheck__(entity_id, scene_layer, clone.horizontal_clone)
        if clone.vertical_clone is not None:
            __recursiveVCloneLayerCheck__(entity_id, scene_layer, clone.vertical_clone)
    except Exception as e:
        print(e)
        assert False
    return True

#asserts an error if a clones layer is not the same as passed in layer
def __recursiveVCloneLayerCheck__(entity_id, scene_layer, clone):
    try:
        if clone.cell.scene_layer != scene_layer:
            print("test_Scene_node - scene layer vclone mismatch: " + str(entity_id))
            assert False
        if clone.vertical_clone is not None:
            __recursiveVCloneLayerCheck__(entity_id, scene_layer, clone.vertical_clone)
    except Exception as e:
        print(e)
        assert False
    return True

#(4.12) SceneNode reference to grid is consistent
def _testNodeGridRefMatchesSceneRef_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._scenes.values():
            sprites = scene._sprites
            scene_layers = scene._scene_layers
            entity_id_by_layer = scene._entity_id_by_layer
            for entity_id, sprite in sprites.items():
                layer_id = entity_id_by_layer[entity_id]
                scene_layer = scene_layers[layer_id]
                scene_grid = scene_layer.scene_grid
                if sprite.grid is not None:
                    if sprite.grid != scene_grid:
                        print("test_Scene_node - grid reference mismatch: " + str(entity_id))
                        assert False
    except Exception as e:
        print(e)
        return False
    return True

#(4.19) World Position correct relative to Ground Position and image
def _testWorldPositionGroundPosition_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            sprites = scene._sprites
            for entity_id, sprite in sprites.items():
                #if the sprite is not in a cell, then we aren't tracking it's position
                if sprite.cell is not None:
                    if sprite.world_position[0] != sprite.ground_position[0]:
                        print("test_Scene_node - ground position x and world position x mismatch, id: "+str(entity_id))
                        assert False
                    expected_wp = sprite.ground_position[1] - sprite.ground_position[2] - sprite.image_coordinates[3] + 1
                    if expected_wp < 0:
                        if sprite.isVisible():
                            if sprite.world_position[1] != 0:
                                print("test_Scene_node - expected a 0 world position, id: "+str(entity_id))
                                assert False
                    else:
                        if expected_wp != sprite.world_position[1]:
                            print("test_Scene_node - world position y mismatch, id: " + str(entity_id))
                            assert False
    except Exception as e:
        print(e)
        return False
    return True

#(4.8) Sprite update flags cleared in active and visible states
#(4.9) Sprite behavior state, image frame match behaviorFSM
def _testSpriteBehaviorState_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._scene_manager._active_scenes:
            __testSpriteBehaviorState__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

def __testSpriteBehaviorState__(game_engine_mock, scene_id):
    try:
        sprites = game_engine_mock._scene_manager._scenes[scene_id]._sprites
        behaviorFSMs = game_engine_mock._behavior_scene_manager._behavior_component_systems[scene_id]._active_behaviorFSMs
        inactive_behaviorFSMs = game_engine_mock._behavior_scene_manager._behavior_component_systems[scene_id]._inactive_behaviorFSMs
        particles = game_engine_mock._physics_scene_manager._particle_component_systems[scene_id]._active_particles
        inactive_particles = game_engine_mock._physics_scene_manager._particle_component_systems[scene_id]._inactive_particles
        for entity_id, sprite in sprites.items():
            if sprite.isVisible() or not sprite.isEthereal():
                #If this is true, then we need to have updated the behavior state/frame
                if _spriteNetworkInActiveCellTest_(sprite) or (sprite.isAlwaysActive() and sprite.isActivated()):
                    try:
                        behaviorFSM = behaviorFSMs[entity_id]
                    except:
                        behaviorFSM = inactive_behaviorFSMs[entity_id]
                    if behaviorFSM.state_has_changed.value:
                        print("test_Scene_node - behaviorFSM.state_has_changed flag not cleared, id: " + str(entity_id))
                        assert False
                    if sprite.frame != behaviorFSM.frame:
                        print("test_Scene_node - behaviorFSM.frame sprite.frame mismatch, id: " + str(entity_id))
                        assert False
                    if sprite.behavior_state_id != behaviorFSM._behavior_state:
                        print("test_Scene_node - behaviorFSM/sprite behavior_state_id mismatch, id: " + str(entity_id))
                        assert False
                    try:
                        particle = particles[entity_id]
                    except:
                        particle = inactive_particles[entity_id]
                    if sprite.cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
                        if particle.has_moved.value:
                            print("test_Scene_node - particle.has_moved flag not cleared, id: " + str(entity_id))
                            assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(4.24) Deactivated or InvisibleEthereal sprites do not have clones
#(4.25) Sprites w/ image in active cell are in active cell or offscreen active
def _testOffscreenActiveNetwork_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            __testOffscreenActiveNetwork__(scene)
    except Exception as e:
        print(e)
        return False
    return True

def __testOffscreenActiveNetwork__(scene):
    try:
        sprites = scene._sprites
        for entity_id, sprite in sprites.items():
            offscreen_active_nodes = sprite.grid.offscreen_active_nodes
            sprite_state_enum = sprite.current_sprite_state.sprite_state_enum
            if sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                if sprite.horizontal_clone is not None or sprite.vertical_clone is not None:
                    print("test_Scene_node - Invisible sprite has clones, id: " + str(entity_id))
                    assert False
                if offscreen_active_nodes.get(entity_id) is not None:
                    print("test_Scene_node - AAInvisible sprite in offscreen actives, id: " + str(entity_id))
                    assert False
                #AAInvisible are not in a cell
                if sprite.cell is not None:
                    print("test_Scene_node - AAInvisible sprite has cell ref id: " + str(entity_id))
                    assert False
                continue
            elif sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL:
                if sprite.horizontal_clone is not None or sprite.vertical_clone is not None:
                    print("test_Scene_node - InvisibleEthereal sprite has clones, id: " + str(entity_id))
                    assert False
            elif not sprite.isActivated():
                if sprite.horizontal_clone is not None or sprite.vertical_clone is not None:
                    print("test_Scene_node - deactivated sprite has clones, id: " + str(entity_id))
                    assert False
                if offscreen_active_nodes.get(entity_id) is not None:
                    print("test_Scene_node - deactivated sprite found in offscreen actives, id: " + str(entity_id))
                    assert False
                if sprite.cell is not None:
                    print("test_Scene_node - inactive sprite has cell ref id: " + str(entity_id))
                    assert False
                #Deativated sprites are not in a cell
                continue
            if sprite.cell is None:
                print("test_Scene_node - Active sprite has no cell reference, id: " + str(entity_id))
                assert False
            if sprite.cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE or \
                            sprite.cell.cell_state_enum == CellStateEnum.CELL_STATE_INVISIBLE:
                if offscreen_active_nodes.get(entity_id) is not None:
                    print("test_Scene_node - Sprite in an active cell is in offscreen actives, id: " + str(entity_id))
                    assert False
            elif sprite.cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                if sprite.current_sprite_state.sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE or \
                        sprite.current_sprite_state.sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE or \
                        sprite.current_sprite_state.sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL:
                    if offscreen_active_nodes.get(entity_id) is None:
                        print("test_Scene_node -AASprite not in active_offscreen cell missing, id: "+ str(entity_id))
                        assert False
                elif _spriteNetworkInActiveCellTest_(sprite):
                    if offscreen_active_nodes.get(entity_id) is None:
                        print("test_Scene_node -sprite network not in active_offscreen in active cell, id: " + str(entity_id))
                        assert False
                else:
                    if offscreen_active_nodes.get(entity_id) is not None:
                        print( "test_Scene_node - Sprite in offscreen actives, no part in active cell, id: " + str(entity_id))
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(4.15) Clone parent reference is consitent
#(4.16) Clones share same entity_id with Sprite
def _testParentCloneRefConsistent_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._scenes.values():
            sprites = scene._sprites
            for entity_id, sprite in sprites.items():
                __cloneParentConsistency__(entity_id, sprite)
    except Exception as e:
        print(e)
        return False
    return True

#recursively check clones and verify their parent ref is always correct
def __cloneParentConsistency__(entity_id, node):
    try:
        if node.entity_id != entity_id:
            print("test_Scene_node - Clone network contains mismatched entity_id")
            assert False
        if node.vertical_clone is not None:
            if node.vertical_clone.parent != node:
                print("test_Scene_node - Vclone parent mismatches, id: "+str(node.entity_id))
                assert False
            #this will either return None, or assert an Error if inconsistency is found
            __cloneParentConsistency__(entity_id, node.vertical_clone)
        if node.horizontal_clone is not None:
            if node.horizontal_clone.parent != node:
                print("test_Scene_node - Hclone parent mismatches, id: "+str(node.entity_id))
                assert False
            __cloneParentConsistency__(entity_id, node.horizontal_clone)
    except Exception as e:
        print(e)
        assert False

#(4.13) Vertical clones do not have horizontal clones
#(4.14) Sprites have clones in expected cells based on image size
#Look at the sprite, world position, and image size.  Verify clones created in all needed cells
    #just find a clone of the correct entity id in the 'grid' of the sprite, but stop if hitting
    #an invisible leading cell, or edge of the world
def _testSpritesCreateNeededClones_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            sprites = scene._sprites
            for entity_id, sprite in sprites.items():
                vclone = sprite.vertical_clone #(4.13)
                while vclone is not None:
                    if vclone.horizontal_clone is not None:
                        print("Vertical clone has a horizontal clone, id" + str(entity_id))
                        assert False
                    vclone = vclone.vertical_clone
                if (sprite.isVisible() or not sprite.isEthereal()) and sprite.current_sprite_state.is_activated:
                    if not __allClonesCreated__(sprite,  sprite.grid):
                        assert False
    except Exception as e:
        print(e)
        return False
    return True

#for _testSpritesCreateNeededClones_
def __allClonesCreated__(sprite, scene_grid):
    try:
        entity_id = sprite.entity_id
        ground_position = sprite.ground_position
        world_position = sprite.world_position
        sprite_width = sprite.image_coordinates[2]
        sprite_height = sprite.image_coordinates[3]
        ground_height_with_z = ground_position[1] - ground_position[2]
        #if the image goes above the map, the image height is clipped
        if (ground_height_with_z+1) - sprite_height < 0:
            sprite_height = ground_height_with_z+1
        if sprite_height <0:
            sprite_height = 0
        cell_width = scene_grid.cell_size[0]
        cell_height = scene_grid.cell_size[1]
        numb_columns = scene_grid.numb_cols
        numb_rows = scene_grid.numb_rows
        start_cell_row =  world_position[1]//cell_height
        start_cell_col =  world_position[0]//cell_width
        if start_cell_col < 0:
            start_cell_col = 0
        if start_cell_col > numb_columns:
            print("test_Scene_node - World position outside of cell columns, id: "+ str(entity_id))
            return False
        if start_cell_row > numb_rows:
            print("test_Scene_node - World position outside of cell rows, id: " + str(entity_id))
            return False
        #based on width of cell, and sprite position, calc number of cell COLUMNS occupied
        start_cell = scene_grid._scene_cells[start_cell_row][start_cell_col]
        cell_offset_x = world_position[0] - start_cell.borders[0]
        image_columns = _ceiling_(sprite_width+cell_offset_x, cell_width)
        #image is clipped at the right boundary of the world
        if start_cell_col + image_columns > numb_columns:
            image_columns = numb_columns - start_cell_col
        #based on width of cell, and sprite position, calc number of cell ROWS occupied
        cell_offset_y = world_position[1] - start_cell.borders[3]
        image_rows = _ceiling_(sprite_height+cell_offset_y, cell_height)
        #if above the world (due to Z offset), still will be placed in a cell (the one it's above)
        if image_rows == 0:
            image_rows = 1
        #image is clipped at the right boundary of the world
        if start_cell_row + image_rows > numb_rows:
            image_rows = numb_rows - start_cell_row
        #verify that the starting cell has the main sprite, and not a clone
        node = _getNodeByEntityIdInCell_(entity_id, start_cell, not sprite.isVisible())
        if node is None:
            print("test_Scene_node - sprite not found in expected cell, id: " + str(entity_id))
            assert False
        if not node:
            print("test_Scene_node - Duplicate entity_id found in cell, id: " + str(entity_id))
            assert False
        if _isCloneBased_(node):
            print("test_Scene_node - clone found but expected sprite, id: " + str(entity_id))
            assert False
        #Iterate through every cell.  Check that sprite/clone is/isn't present as expected
        for row in range (0, numb_rows):
            included_row = False
            if start_cell_row <= row < start_cell_row + image_rows:
                included_row = True
            for col in range(0, numb_columns):
                curent_cell = scene_grid._scene_cells[row][col]
                node = _getNodeByEntityIdInCell_(entity_id, curent_cell, not sprite.isVisible())
                if node is not None and node == False:
                    print("test_Scene_node, duplicate id detected in cell, id: " + str(entity_id))
                    assert False
                #If we are within the cells which the sprite is visible in
                if start_cell_col <= col < start_cell_col + image_columns and included_row:
                    #if we are in range, and have not hit invisible leading, we expect to find something
                    if node is None:
                        print("test_Scene_node, node not found in expected cell, id: "+str(entity_id))
                        assert False
                    if row == start_cell_row:
                        #we are in the cell origin
                        if col == start_cell_col:
                            if _isCloneBased_(node):
                                print("test_Scene_node - clone found but expected sprite, id: " + str(entity_id))
                                assert False
                        #we are in the first row, which are the horizontal clones
                        elif not _isHorizontalCloneBased_(node):
                                print("test_Scene_node - expected a horizontal clone, id: " + str(entity_id))
                                assert False
                #Outside of the image range, sprite/clone should not be found
                else:
                    if node is not None:
                        print("test_Scene_node - expected node to be none, id: " + str(entity_id))
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

#for _testSpriteRenderCoordinates_
#(4.1) Sprite Render Coordinates fully covered
#(4.2) Render Coordinates clipped to edge of world
#(4.3) Sprite/Clone cell ref consistent with cell LL
#(4.4) Clones share same Ground Position with Sprite
#(4.5) No Negative values in Render Coordinates
#(4.6) Sprites/Clones do not overlap and edges line up
def _testSpriteRenderCoordinates_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            sprites = scene._sprites.values()
            for sprite in sprites:
                if (sprite.isVisible() or not sprite.isEthereal()) and sprite.cell is not None:
                    test_sprite = _getNodeByEntityIdInCell_(sprite.entity_id, sprite.cell, not sprite.isVisible()) #(57)
                    if test_sprite != sprite:
                        print("test_Scene_node - node's cell ref does not return cell with that node, id: "
                              + str(sprite.entity_id)) #(4.4)
                        assert False
                if not __calcSpriteRenderCoordinatesRecursive__(sprite):
                    assert False
    except Exception as e:
        print(e)
        return False
    return True

def __calcSpriteRenderCoordinatesRecursive__(sprite):
    try:
        if not sprite.current_sprite_state.is_visible:
            return True
        if not sprite.current_sprite_state.is_activated:
            return True
        # This must be fully and exactly covered with no overlap by render_coordinates
        image_coordinates = sprite.image_coordinates
        render_coordinates = sprite.image_render_coordinates
        if render_coordinates[0] < 0:
            print("test_Scene_node - render coord[0] is negative, id: " + str(sprite.entity_id))
            assert False
        if render_coordinates[1] < 0:
            print("test_Scene_node - render coord[1] is negative, id: " + str(sprite.entity_id))
            assert False
        if render_coordinates[2] < 0:
            print("test_Scene_node - render coord[2] is negative, id: " + str(sprite.entity_id))
            assert False
        # if we end up with negative height on the image, we are out of bounds and won't be rendered
        if sprite.ground_position[2] < 0:
            print("test_Scene_node - negative z offset not supported, id: " + str(sprite.entity_id))
            assert False
        if render_coordinates[3] <= 0:
            if sprite.ground_position[2] == 0:
                print("test_Scene_node - We should only have a negative RC if there is a Z offset, id: " +
                      str(sprite.entity_id))
                assert False
            if sprite.ground_position[1] - sprite.ground_position[2] >= 0:
                print("test_Scene_node - negative RC with part of sprite visible, id" +
                      str(sprite.entity_id))
                assert False
            if sprite.vertical_clone is not None:
                print("test_Scene_node - negative RC means that the sprite is above the map,"
                      " there should be no vertical clones" + str(sprite.entity_id))
                assert False
            return True  # nothing worth checking, we are not visible
        if sprite.world_position[1] < 0:
            print("test_Scene_node - Image not clipped vertically at world border, id: " + str(sprite.entity_id))
            assert False
        render_x_position = render_coordinates[0]
        render_y_position = render_coordinates[1]
        if render_x_position != image_coordinates[0]:
            print("test_Scene_node - Sprite render x does not start at left side of image, id: " + str(sprite.entity_id))
            assert False
        total_width = image_coordinates[2]
        total_height = image_coordinates[3]
        # The render coordinates are clipped if going above map, also subtract the Z-offset
        if total_height - 1 > (sprite.ground_position[1] - sprite.ground_position[2]):
            clipped_amount = total_height - (sprite.ground_position[1] - sprite.ground_position[2]) - 1
            total_height = sprite.ground_position[1] + 1 - sprite.ground_position[2]
            if render_y_position != image_coordinates[1] + clipped_amount:
                print("test_Scene_node - Sprite render Y not clipped correctly, id: " + str(sprite.entity_id))
                assert False
        elif render_y_position != image_coordinates[1]:
            print("test_Scene_node - Sprite render coords do not start at top corner of image coords, id: " + str(
                sprite.entity_id))
            assert False
        if sprite.world_position[0] + sprite.image_render_coordinates[2] - 1> sprite.cell.borders[2]:
            print("test_Scene_node - Sprite render width exceeds cell, id: " + str(sprite.entity_id))
            assert False
        if sprite.world_position[1] + sprite.image_render_coordinates[3] - 1> sprite.cell.borders[1]:
            print("test_Scene_node - Sprite render width exceeds cell, id: " + str(sprite.entity_id))
            assert False
        ### Begin checking the image coordinates ###
        #Vertical first
        render_height_covered = sprite.image_render_coordinates[3]
        if render_height_covered > total_height:
            print("test_Scene_node - Sprite RC height > IC height, id: " + str(sprite.entity_id))
            assert False
        elif render_height_covered == total_height:
            if sprite.vertical_clone is not None:
                print("test_Scene_node - vlone on sprite with RC height covered, id: " + str(sprite.entity_id))
                assert False
        else:
            # Check to see if we are the bottom cell of the map
            if sprite.cell.borders[1] + 1 >= sprite.grid.world_size[1]:
                # verify it is clipped at exactly the bottom of the cell
                if sprite.world_position[1] + sprite.image_render_coordinates[3] - 1 != sprite.cell.borders[1]:
                    print("test_Scene_node - on furthest bottom cell, height not covered, image should cover cell, id: " + str(sprite.entity_id))
                    assert False
            else:
                if sprite.world_position[1] + sprite.image_render_coordinates[3] - 1 != sprite.cell.borders[1]:
                    print("test_Scene_node - Sprite render height clipped short of cell border, id: " + str(sprite.entity_id))
                    assert False
                else:
                    if sprite.vertical_clone is None:
                        print("test_Scene_node - no vlone on spriteRC height not covered, id: " + str(sprite.entity_id))
                        assert False
                    if not __checkVerticalCloneCoordRecursive__(sprite.vertical_clone, sprite, total_height, render_height_covered):
                        assert False
        #Horizontal next
        render_width_covered = sprite.image_render_coordinates[2]
        if render_width_covered > total_width:
            print("test_Scene_node - Sprite RC width > IC width, id: " + str(sprite.entity_id))
            assert False
        elif render_width_covered == total_width:
            if sprite.horizontal_clone is not None:
                print("test_Scene_node - hclone on sprite with RC width covered, id: " + str(sprite.entity_id))
                assert False
        else:
            if sprite.cell.borders[2] + 1 >= sprite.grid.world_size[0]:
                # verify it is clipped at exactly the right of the cell
                if sprite.world_position[0] + sprite.image_render_coordinates[2] - 1 != sprite.cell.borders[2]:
                    print("test_Scene_node - on furthest right cell, width not covered,image should cover cell, id: " + str(sprite.entity_id))
                    assert False
            else:
                if sprite.world_position[0] + sprite.image_render_coordinates[2] - 1 != sprite.cell.borders[2]:
                    print("test_Scene_node - Sprite render width clipped short of cell border, id: " + str(sprite.entity_id))
                    assert False
                if sprite.horizontal_clone is None:
                    print("test_Scene_node - no hclone on sprite RC width not covered, id: " + str(sprite.entity_id))
                    assert False
                if not __checkHorizontalRenderCoordRecursive__(sprite.horizontal_clone, sprite, total_height, total_width, render_width_covered):
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

def __checkVerticalCloneCoordRecursive__(vclone, parent, total_height, render_height_covered):
    try:
        if vclone.ground_position != parent.ground_position:
            print("test_Scene_node - vlone gp mismatch, id: " + str(vclone.entity_id))
            assert False
        if vclone.entity_id != parent.entity_id:
            print("test_Scene_node - vlone entity_id mismatch, id: " + str(vclone.entity_id))
            assert False
        #Ensure that the vclone image is adjacent to the parent
        if vclone.world_position[1] != vclone.cell.borders[3]:
            print("test_Scene_node - Vertical clone does not start at cell boundary, id: " + str(vclone.entity_id))
            assert False
        if vclone.world_position[0] != parent.world_position[0]:
            print("test_Scene_node - Vertical clone has different world X than parent, id: " + str(vclone.entity_id))
            assert False
        if vclone.image_render_coordinates[0] != parent.image_render_coordinates[0]:
            print("test_Scene_node - V clone image X position not same as parent, id: " + str(vclone.entity_id))
            assert False
        if vclone.image_render_coordinates[2] != parent.image_render_coordinates[2]:
            print("test_Scene_node - Vertical clone has different width than parent, id: " + str(vclone.entity_id))
            assert False
        if vclone.image_render_coordinates[1] != parent.image_render_coordinates[1] + parent.image_render_coordinates[3]:
            print("test_Scene_node - V clone image Y position adjacent to parent, id: " + str(vclone.entity_id))
            assert False
        if vclone.world_position[1] + vclone.image_render_coordinates[3] - 1 > vclone.cell.borders[1]:
            print("test_Scene_node - vclone render height passes cell border, id: " + str(vclone.entity_id))
            assert False
        #add the new image height
        render_height_covered = render_height_covered + vclone.image_render_coordinates[3]

        if render_height_covered > total_height:
            print("test_Scene_node vclone - Sprite RC height > IC height, id: " + str(vclone.entity_id))
            assert False
        elif render_height_covered == total_height:
            if vclone.vertical_clone is not None:
                print("test_Scene_node vclone - on sprite with RC height covered, id: " + str(vclone.entity_id))
                assert False
            return True #SUCCESS!
        else:
            # Check to see if we are the bottom cell of the map
            if vclone.cell.borders[1] + 1 >= vclone.grid.world_size[1]:
                # verify it is clipped at exactly the bottom of the cell
                if vclone.world_position[1] + vclone.image_render_coordinates[3] - 1 != vclone.cell.borders[1]:
                    print("test_Scene_node vclone- on furthest bottom cell, height not covered, image should cover cell, id: " + str(vclone.entity_id))
                    assert False
                return True #SUCCESS!
            else:
                if vclone.world_position[1] + vclone.image_render_coordinates[3] - 1 != vclone.cell.borders[1]:
                    print("test_Scene_node - vclone height clipped short of cell border, id: " + str(vclone.entity_id))
                    assert False
                else:
                    if vclone.vertical_clone is None:
                        print("test_Scene_node - no vlone on spriteRC height not covered, id: " + str(vclone.entity_id))
                        assert False
                    return __checkVerticalCloneCoordRecursive__(vclone.vertical_clone, vclone, total_height, render_height_covered)
    except Exception as e:
        print(e)
        assert False

def __checkHorizontalRenderCoordRecursive__(hclone, parent, total_render_height, total_width, render_width_covered):
    try:
        if hclone.ground_position != parent.ground_position:
            print("test_Scene_node - vlone gp mismatch, id: " + str(hclone.entity_id))
            assert False
        if hclone.entity_id != parent.entity_id:
            print("test_Scene_node - vlone entity_id mismatch, id: " + str(hclone.entity_id))
            assert False
        #Ensure that the vclone image is adjacent to the parent
        if hclone.world_position[0] != hclone.cell.borders[0]:
            print("test_Scene_node - hclone does not start at cell boundary, id: " + str(hclone.entity_id))
            assert False
        if hclone.world_position[1] != parent.world_position[1]:
            print("test_Scene_node - hclone clone has different world Y than parent, id: " + str(hclone.entity_id))
            assert False
        if hclone.image_render_coordinates[1] != parent.image_render_coordinates[1]:
            print("test_Scene_node - hclone image Y position not same as parent, id: " + str(hclone.entity_id))
            assert False
        if hclone.image_render_coordinates[3] != parent.image_render_coordinates[3]:
            print("test_Scene_node - hclone image has different height than parent, id: " + str(hclone.entity_id))
            assert False
        if hclone.image_render_coordinates[0] != parent.image_render_coordinates[0] + parent.image_render_coordinates[2]:
            print("test_Scene_node - hclone image X position adjacent to parent, id: " + str(hclone.entity_id))
            assert False
        if hclone.world_position[1] + hclone.image_render_coordinates[3] - 1> hclone.cell.borders[1]:
            print("test_Scene_node - hclone render width exceeds cell, id: " + str(hclone.entity_id))
            assert False
        #check the height, and for Vclones
        render_height_covered = hclone.image_render_coordinates[3]
        if render_height_covered > total_render_height:
            print("test_Scene_node - hclone RC height > IC height, id: " + str(hclone.entity_id))
            assert False
        elif render_height_covered == total_render_height:
            if hclone.vertical_clone is not None:
                print("test_Scene_node - vlone on hclone with RC height covered, id: " + str(hclone.entity_id))
                assert False
        else:
            # Check to see if we are the bottom cell of the map
            if hclone.cell.borders[1] + 1 >= hclone.grid.world_size[1]:
                #If we prevent the node Ground Position from being beyond bottom border of world, we will never get here
                # verify it is clipped at exactly the bottom of the cell
                if hclone.world_position[1] + hclone.image_render_coordinates[3] - 1 != hclone.cell.borders[1]:
                    print("test_Scene_node hclone- on furthest bottom cell, height not covered, image should cover cell, id: " + str(hclone.entity_id))
                    assert False
            else:
                if hclone.world_position[1] + hclone.image_render_coordinates[3] - 1 != hclone.cell.borders[1]:
                    print("test_Scene_node - hclone render height clipped short of cell border, id: " + str(hclone.entity_id))
                    assert False
                else:
                    if hclone.vertical_clone is None:
                        print("test_Scene_node hclone- no vlone on spriteRC height not covered, id: " + str(hclone.entity_id))
                        assert False
                    if not __checkVerticalCloneCoordRecursive__(hclone.vertical_clone, hclone, total_render_height, render_height_covered):
                        assert False
        #Horizontal next
        render_width_covered += hclone.image_render_coordinates[2]
        if render_width_covered > total_width:
            print("test_Scene_node - Sprite RC width > IC width, id: " + str(hclone.entity_id))
            assert False
        elif render_width_covered == total_width:
            if hclone.horizontal_clone is not None:
                print("test_Scene_node - hclone on hclone with RC width covered, id: " + str(hclone.entity_id))
                assert False
            return True  # SUCCESS!
        else:
            if hclone.cell.borders[2] + 1 >= hclone.grid.world_size[0]:
                # verify it is clipped at exactly the right of the cell
                if hclone.world_position[0] + hclone.image_render_coordinates[2] - 1 != hclone.cell.borders[2]:
                    print("test_Scene_node - on furthest right cell, width not covered,image should cover cell, id: " + str(hclone.entity_id))
                    assert False
                return True #SUCCESS!
            else:
                if hclone.world_position[0] + hclone.image_render_coordinates[2] - 1 != hclone.cell.borders[2]:
                    print("test_Scene_node - hclone render width clipped short of cell border, id: " + str(hclone.entity_id))
                    assert False
                if hclone.horizontal_clone is None:
                    print("test_Scene_node - no hclone on hclone RC width not covered, id: " + str(hclone.entity_id))
                    assert False
                return __checkHorizontalRenderCoordRecursive__(hclone.horizontal_clone, hclone, total_render_height, total_width, render_width_covered)
    except Exception as e:
        print(e)
        assert False

#(4.16) Clones are not both invisible and ethereal
#(4.17) Clones have same ethereal/visibility state as parent
def _testCloneParentVisibilityMatches_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._scenes.values():
            for entity_id, sprite in scene._sprites.items():
                is_visible = sprite.isVisible()
                is_ethereal = sprite.isEthereal()
                if not __recursiveCloneVisibilityCheck__(sprite, is_visible, is_ethereal):
                    print("test_Scene_node - clone/sprite mismatch visible/ethereal, id: ", entity_id)
                    assert False
    except Exception as e:
        print(e)
        return False
    return True

def __recursiveCloneVisibilityCheck__(node, is_visible, is_ethereal):
    try:
        if node.isVisible() != is_visible:
            return False
        if node.isEthereal() != is_ethereal:
            return False
        if node.horizontal_clone is not None:
            if node.horizontal_clone.isEthereal() and (not node.horizontal_clone.isVisible()):
                print("test_Scene_node - clone is both invisible and ethereal")
                assert False
            if not __recursiveCloneVisibilityCheck__(node.horizontal_clone, is_visible, is_ethereal):
                return False
        if node.vertical_clone is not None:
            if node.vertical_clone.isEthereal() and (not node.vertical_clone.isVisible()):
                print("test_Scene_node - clone is both invisible and ethereal")
                assert False
            if not __recursiveCloneVisibilityCheck__(node.vertical_clone, is_visible, is_ethereal):
                return False
    except Exception as e:
        print(e)
        assert False
    return True
