from Game_Scene.Scene_Cell.Scene_cell import CellStateEnum
from Entity_manager import ACTIVATED_INDEX, ALWAYS_ACTIVE_INDEX
from Game_Scene.Test.Test_Suites.test_Scene_functions import _isCloneBased_, _spriteNetworkInActiveCellTest_
from Scene_Node.Sprite_node import SpriteNode
from Scene_Node.Clone_node import VerticalSpriteClone, HorizontalSpriteClone
from Sprite_state import SpriteStateEnum

LEFT = 0
BOTTOM = 1
RIGHT = 2
TOP = 3

#(2.16) scene_cell metadata mirrors master_cell
def _testCellMetaDataMatchesMaster_(game_engine_mock):
    try:
        for scene_id, scene in game_engine_mock._scene_manager._scenes.items():
            master_cells = scene._scene_master_grid.master_cells
            for layer_id, scene_layer in scene._scene_layers.items():
                scene_cells = scene_layer.scene_grid._scene_cells
                if len(scene_cells) != len(master_cells):
                    print("test_Scene_grid - scene/mastergrid row ct mismatch, ids: "+ str(scene_id) + ", " + str(layer_id))
                    assert False
                if len(scene_cells[0]) != len(master_cells[0]):
                    print("test_Scene_grid - scene/mastergrid col ct mismatch, ids: "+ str(scene_id) + ", " + str(layer_id))
                    assert False
                for row in range(0, len(scene_cells)):
                    for col in range(0, len(scene_cells[0])):
                        scene_cell = scene_cells[row][col]
                        master_cell = master_cells[row][col]
                        if scene_cell.master_cell != master_cell:
                            print("test_Scene_grid - ref mismatch")
                            print(scene_id, layer_id, row, col)
                            assert False
                        if scene_cell.cell_id != master_cell.cell_id:
                            print("test_Scene_grid - cell_id mismatch")
                            print(scene_id, layer_id, row, col)
                            assert False
                        if scene_cell.borders != master_cell.borders:
                            print("test_Scene_grid - borders mismatch")
                            print(scene_id, layer_id, row, col)
                            assert False
                        if scene_cell.size != master_cell.size:
                            print("test_Scene_grid - size mismatch")
                            print(scene_id, layer_id, row, col)
                            assert False
                        if scene_cell.cell_state_enum != master_cell.cell_state_enum:
                            print("test_Scene_grid - cell_state_enum mismatch")
                            print(scene_id, layer_id, row, col)
                            assert False
    except Exception as e:
        print(e)
        return False
    return True

#(2.15) No Duplicate clone/sprite references in Grid
def _testAllEntitiesInGridUnique_(game_engine_mock):
    try:
        # Store every entity in all scenes.  Check for any duplicate references
        entities = list()
        for scene in game_engine_mock._scene_manager._scenes.values():
            for scene_layer in scene._scene_layers.values():
                entities = __testAllEntitiesInGridUnique__(scene_layer, entities)
    except Exception as e:
        print(e)
        return False
    return True


def __testAllEntitiesInGridUnique__(scene_layer, entities):
    try:
        grid = scene_layer.scene_grid
        scene_cells = grid._scene_cells
        for node in grid.always_active_invisible_ethereal_nodes.values():
            if node in entities:
                print("Duplicate entity found in always_active_invisible_ethereal_nodes")
                assert False
            entities.append(node)
        for cell_row in scene_cells:
            for cell in cell_row:
                entities = __cellGetEntities__(cell, entities)
        return entities
    except Exception as e:
        print(e)
        assert False

#(2.10) Sum of cell sizes equals world size
#(2.11) Cell borders are aligned, cell sizes are consistent
#(2.12) All cell rows have same number of columns
#(2.13) Grid.numb_rows/cols consistent with cells list
#(2.14) Tile size is less than cell size and is a multiple of cell size
def _testCellBordersSizes_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._scenes.values():
            for scene_layer in scene._scene_layers.values():
                __testCellBordersSizes__(scene_layer)
    except Exception as e:
        print(e)
        return False
    return True

def __testCellBordersSizes__(scene_layer):
    try:
        if len(scene_layer.scene_grid.master_grid._cameras) == 0:
            return True
        grid = scene_layer.scene_grid
        master_grid = grid.master_grid
        scene_cells = grid._scene_cells
        numb_rows = len(scene_cells)
        # (2.13)
        if numb_rows != master_grid.numb_rows:
            print("test_Scene_grid - numb rows doesn't match list size")
            assert False
        numb_cols = len(master_grid.master_cells[0])
        if numb_cols != master_grid.numb_cols:
            print("test_Scene_grid - numb cols doesn't match list size")
            assert False
        # (2.12)
        row = 0
        while row < numb_rows:
            if len(scene_cells[row]) != numb_cols:
                print("test_Scene_grid - numb cols different on row "+str(row))
                assert False
            row+=1
        # (2.14)
        if master_grid.tile_size[0] > master_grid.cell_size[0]:
            print("test_Scene_grid - tile size x larger than cell size x")
            assert False
        if master_grid.tile_size[1] > master_grid.cell_size[1]:
            print("test_Scene_grid - tile size y larger than cell size y")
            assert False
        if master_grid.cell_size[0] % master_grid.tile_size[0] != 0:
            print("test_Scene_grid - tile size x not multiple of cell size x")
            assert False
        if master_grid.cell_size[1] % master_grid.tile_size[1] != 0:
            print("test_Scene_grid - tile size y not multiple of cell size y")
            assert False

        # (2.11) Cell borders are aligned, cell sizes are consistent
        #(2.10) Sum of cell sizes equals world size
        world_size = master_grid.world_size
        #go rows x cols first, then go cols x row
        #this is to ensure that the borders vertically and horizontlly are 'straight'
        row = 0
        height_covered = 0
        while row < numb_rows:
            current_top_border = scene_cells[row][0].borders[TOP]
            current_bottom_border = scene_cells[row][0].borders[BOTTOM]
            col = 0
            width_covered = 0
            while col < numb_cols:
                borders = scene_cells[row][col].borders
                if borders[TOP] != current_top_border:
                    print("test_Scene_grid - top border mismatch")
                    assert False
                if borders[BOTTOM] != current_bottom_border:
                    print("test_Scene_grid - top border mismatch")
                    assert False
                if borders[TOP] != height_covered:
                    print("test_Scene_grid - top border mismatch")
                    assert False
                if borders[BOTTOM] - borders[TOP] +1 != master_grid.cell_size[1]:
                    if borders[BOTTOM] - borders[TOP] + 1 + height_covered != world_size[1]:
                        print("test_Scene_grid - cell height mismatch")
                        assert False
                if borders[RIGHT] - borders[LEFT] != master_grid.cell_size[0] -1:
                    if borders[RIGHT] - borders[LEFT] + width_covered + 1 != world_size[0]:
                        print("test_Scene_grid - cell width mismatch")
                        assert False
                width_covered += borders[RIGHT] - borders[LEFT] + 1
                col+=1
            if width_covered != world_size[0]:
                print("test_Scene_grid - world width mismatch")
                assert False
            height_covered += current_bottom_border - current_top_border + 1
            row+=1
        if height_covered != world_size[1]:
            print("test_Scene_grid - world height mismatch")
            assert False
        #height and width is consitent, just make sure all cols have the same right/left border
        col = 0
        while col < numb_cols:
            current_left_border = scene_cells[0][col].borders[LEFT]
            current_right_border = scene_cells[0][col].borders[RIGHT]
            row = 0
            while row < numb_rows:
                borders = scene_cells[row][col].borders
                if borders[RIGHT] != current_right_border:
                    print("test_Scene_grid - right border mismatch")
                    assert False
                if borders[LEFT] != current_left_border:
                    print("test_Scene_grid - left border mismatch")
                    assert False
                row+=1
            col+=1
    except Exception as e:
        print(e)
        assert False
    return True

#(2.17) All cell_ids in offscreen_inactives are inactive cells
#(2.18) Sprite in offscreen_actives is 'always_active' or has active dep
#(2.19) Sprite in offscreen_actives is not in an active cell
#(2.20) No clones in offscreen_inactives
#(2.21) Inactive sprites do not contain references to a cell
#(2.22) All offscreen active sprites are active
#(2.23) All AAInvisible sprites in a_a_invisible list, no others in list
#(2.24) All sprites that should be in offscreen_inactives found
#(2.25) No duplicate entity_ids in offscreen_inactives
def _testOffScreenActives_(game_engine_mock):
    try:
        for scene_id in game_engine_mock._active_scene_ids:
            __testOffScreenActives__(game_engine_mock, scene_id)
    except Exception as e:
        print(e)
        return False
    return True

def __testOffScreenActives__(game_engine_mock, scene_id):
    try:
        active_scene = game_engine_mock._scene_manager._scenes[scene_id]
        entity_status_lists = game_engine_mock._entity_scene_manager._entity_systems[scene_id]._entity_status_lists
        sprites = active_scene._sprites
        for scene_layer in active_scene._scene_layers.values():
            ___testOffScreenActives___(scene_layer, entity_status_lists, sprites)
        #check all sprites, and verify that sprites which should be in the offscreen actives are
        #make sure inactive sprites are not in the grid
        #make sure AAInvisibleEthereal sprites not in the grid
        sprites = active_scene._sprites
        for entity_id, sprite in sprites.items():
            entity_status = entity_status_lists[entity_id]
            if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                if not __foundInAAInvisibleEthereals__(active_scene, entity_id):
                    print("test_Scene_grid - AAInvisible sprite not in the always_active_invisible_ethereal_nodes list, id: " + str(entity_id))
                    assert False
                if sprite.cell is not None:
                    print("test_Scene_grid - AAInvisible sprite contain a cell ref, id: " + str(entity_id))
                    assert False
            elif __foundInAAInvisibleEthereals__(active_scene, entity_id):
                print("test_Scene_grid - non AAInvisible is in always_active_invisible_ethereal_nodes list 1, id: " + str(entity_id))
                assert False
            # (40) Inactive sprites do not contain references to a cell or the grid
            if not sprite.isActivated():
                if sprite.cell is not None:
                    print("test_Scene_grid - deactiveated sprite has a cell ref: " + str(entity_id))
                    assert False
            #AAInvisibleEthereal sprites will not have a cell ref
            elif sprite.cell is not None and not sprite.cell.isActive():
                #if any dependants are in an active cell, or the entity is set to always active
                if _spriteNetworkInActiveCellTest_(sprites[entity_id]) or \
                        entity_status[ALWAYS_ACTIVE_INDEX]:
                    if not __foundInOffscreenActives__(active_scene, entity_id):
                        print("test_Scene_grid - expected to see sprite in offscreen_active_nodes, id:  " + str(entity_id))
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

def ___testOffScreenActives___(scene_layer, entity_status_lists, sprites):
    try:
        offscreen_active_nodes = scene_layer.scene_grid.offscreen_active_nodes
        always_active_invisible_ethereal_nodes = scene_layer.scene_grid.always_active_invisible_ethereal_nodes
        #verify in correct list
        #to track all entity ids and verify no dupes
        entity_ids_found = list()
        for entity_id, node in offscreen_active_nodes.items():
            if entity_id in entity_ids_found:
                print("test_Scene_grid - duplicate entity_id in offscreen_active_nodes, id: " + str(entity_id))
                assert False
            entity_ids_found.append(entity_id)
            if _isCloneBased_(node):
                print("test_Scene_grid - Clone is in the offscreen actives, id: " + str(entity_id))
                assert False
            if not node.isActivated():
                print("test_Scene_grid - deactivated node in the offscreen actived, id: " + str(entity_id))
                assert False
            if node.cell.isActive():
                print("test_Scene_grid - SceneNode in offscreen actives is in an active cell, id: " + str(entity_id))
                assert False
            entity_status = entity_status_lists[entity_id]
            if not entity_status[ACTIVATED_INDEX]:
                print("test_Scene_grid - Deactivated node in the offscreen_active_nodes dict, id: " + str(entity_id))
                assert False
            if node.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                print("test_Scene_grid - AAInvisibleEthereal node in the offscreen_active_nodes dict, id: " + str(entity_id))
                assert False
            if entity_status[ALWAYS_ACTIVE_INDEX]:
                pass #this is good enough reason to be on the list
            else: #if not set to Always Active, then a clone or dependant should be in an active cell
                if not _spriteNetworkInActiveCellTest_(sprites[entity_id]):
                    print("test_Scene_grid - SceneNode in offscreen_active_nodes not always active "
                          "and no dependants in active cells, id: " + str(entity_id))
                    assert False
        #verify AAInvisible sprites have no cell ref
        #verify all sprites in always_active_invisible_ethereal_nodes list are AAInvisible state
        for entity_id, sprite in always_active_invisible_ethereal_nodes.items():
            if sprite.cell is not None:
                print("test_Scene_grid - AAInvisible sprite contains a cell ref, id: " + str(entity_id))
                assert False
            if not sprite.isActivated():
                print("test_Scene_grid - AAInvisible sprite is not Activated, id: "+ str(entity_id))
                assert False
            if not sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                print("test_Scene_grid - non AAInvisibleEthereal is in always_active_invisible_ethereal_nodes list 2, id: " + str(entity_id))
                assert False
    except Exception as e:
        print(e)
        assert False
    return True

#Checks the AAinvisible lists in all layers, returning true if entity_id found, else false
def __foundInAAInvisibleEthereals__(scene, entity_id):
    try:
        for scene_layer in scene._scene_layers.values():
            if scene_layer.scene_grid.always_active_invisible_ethereal_nodes.get(entity_id) is not None:
                return True
        return False
    except Exception as e:
        print(e)
        assert False

#Checks the offscreen_actives lists in all layers, returning true if entity_id found, else false
def __foundInOffscreenActives__(scene, entity_id):
    try:
        for scene_layer in scene._scene_layers.values():
            if scene_layer.scene_grid.offscreen_active_nodes.get(entity_id) is not None:
                return True
        return False
    except Exception as e:
        print(e)
        assert False

#(2.1) All nodes in the grid are in the scene layer
#(2.2) Grids references correct scene layer
def _testEntityInGridInDict_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._scenes.values():
            sprite_dict = scene._sprites
            for scene_layer in scene._scene_layers.values():
                __testEntityInGridInDict__(scene_layer, sprite_dict)
    except Exception as e:
        print(e)
        return False
    return True

def __testEntityInGridInDict__(scene_layer, sprite_dict):
    try:
        scene_grid = scene_layer.scene_grid
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                if __findSpriteInDict__(cell, sprite_dict) is False:
                    print("test_Scene_grd - DynamicGrid.__findSpriteInDict__() sprite in the grid not in dict, cell: " + str(cell.cell_id))
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(2.3) No duplicate entity_ids in a cell
#(2.4) Clones in correct cell relative to parent
#(2.5) All expected Clones found
def _testCloneParentRelationship_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            for scene_layer in scene._scene_layers.values():
                __testCloneParentRelationship__(scene_layer)
    except Exception as e:
        print(e)
        assert False
    return True

def __testCloneParentRelationship__(scene_layer):
    try:
        scene_grid = scene_layer.scene_grid
        # add every id to a list, ensure that a sprite instance is the first time we see it
        entity_ids_in_grid = list()
        # create a 2d grid of expected clones.  Add entity_id's to the corresponing cell list
        expected_hclones_grid = list()
        expected_vclones_grid = list()

        for row in range(scene_grid.numb_rows):
            expected_hclones_row = list()
            expected_vclones_row = list()
            for col in range(scene_grid.numb_cols):
                expected_hclones_row.append(list())
                expected_vclones_row.append(list())
            expected_hclones_grid.append(expected_hclones_row)
            expected_vclones_grid.append(expected_vclones_row)

        for row in range(scene_grid.numb_rows):
            for col in range(scene_grid.numb_cols):
                cell = scene_grid._scene_cells[row][col]
                current_node = cell.head
                linked_list_done = False #Set true once the main LL is empty
                #If the Linked list is empty, check the invisible nodes
                if current_node is None:
                    current_node = cell.invisible_head
                    linked_list_done = True #There are no visible nodes in this cell
                entity_ids_in_cell = list()
                while current_node is not None:
                    if current_node.entity_id in entity_ids_in_cell:
                        print("test_Scene_grid - Duplicate entity_id within same cell.  Cell: " +
                              str(cell.cell_id) + ", entity_id: " + str(current_node.entity_id))
                        assert False
                    entity_ids_in_cell.append(current_node.entity_id)
                    # verify that existing clones are in correct cells
                        # (by referencing the class directly, we protect against refactor)
                    if current_node.__class__.__name__ == SpriteNode.__name__:
                        if current_node.entity_id in entity_ids_in_grid:
                            print("test_Scene_grid - Duplicate entity_id for Sprite instance in grid, " + str(current_node.entity_id))
                            assert False
                    elif current_node.__class__.__name__ == HorizontalSpriteClone.__name__:
                        if current_node.entity_id not in expected_hclones_grid[row][col]:
                            print("test_Scene_grid - Expected to see a horizontal clone in this cell: " + str(current_node.entity_id))
                            assert False
                        # we remove the expected as we find them, after we check all cells verify no leftovers
                        expected_hclones_grid[row][col].remove(current_node.entity_id)
                    elif current_node.__class__.__name__ == VerticalSpriteClone.__name__:
                        if current_node.entity_id not in expected_vclones_grid[row][col]:
                            print("test_Scene_grid - Expected to see a vertical clone in this cell: " + str(current_node.entity_id))
                            assert False
                        expected_vclones_grid[row][col].remove(current_node.entity_id)
                        if current_node.horizontal_clone is not None:
                            print("test_Scene_grid - Vertical clone has a horizontal clone, " + str(current_node.entity_id))
                            assert False
                    # add expected clones to future cells
                    if current_node.horizontal_clone is not None:
                        if col == scene_grid.numb_cols - 1:
                            print("test_Scene_grid - Sprite in last column has horizontal clone: " + str(current_node.entity_id))
                            assert False
                        # when we are in the next cell, we should find this clone
                        expected_hclones_grid[row][col + 1].append(current_node.entity_id)
                    if current_node.vertical_clone is not None:
                        if row == scene_grid.numb_rows - 1:
                            print("test_Scene_grid - Sprite in last row has vertical clone: " + str(current_node.entity_id))
                            assert False
                        expected_vclones_grid[row + 1][col].append(current_node.entity_id)
                    # when we see a spriteInstance, it should be the first occurence of it's entity ID
                    entity_ids_in_grid.append(current_node.entity_id)
                    current_node = current_node.next_node
                    #If we iterated through the visible linked list, start checking the invisible linked list:
                    if current_node is None and not linked_list_done:
                        linked_list_done = True
                        current_node = cell.invisible_head #will drop out of the loop immediately if this is also None

        ### Part 2 ###
        # make sure all expected clones were found
        found_all_clones = True
        for row in range(scene_grid.numb_rows):
            for col in range(scene_grid.numb_cols):
                if len(expected_hclones_grid[row][col]) > 0:
                    print("test_Scene_grid - Did not find following expected hclone(s) in cell ("
                          + str(row) + "," + str(col) + ")")
                    for entity_id in expected_hclones_grid[row][col]:
                        print(entity_id)
                    found_all_clones = False
                if len(expected_vclones_grid[row][col]) > 0:
                    print("test_Scene_grid - Did not find following expected vclone(s) in cell ("
                          + str(row) + "," + str(col) + ")")
                    for entity_id in expected_vclones_grid[row][col]:
                        print(entity_id)
                    found_all_clones = False
        if not found_all_clones:
            print("test_Scene_grid - did not find all expected clones")
            assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(2.9) Cells not a part of any camera active range are Inactive
def _testMasterCellsInactiveState_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            # may need to make  another inner loop if we have multiple master grids in a scene (for parallax scrolling)
            scene_master_grid = scene._scene_master_grid
            __testMasterCellsInactiveState__(scene_master_grid)
    except Exception as e:
        print(e)
        return False
    return True

#This checks that all cells are correct state based on camera ranges
#This test assumes that the cameras have the correct ranges
# _testMasterCellsActiveState_ checks the camera ranges
def __testMasterCellsInactiveState__(scene_master_grid):
    try:
        cameras = list(scene_master_grid._cameras.values())
        master_cells = scene_master_grid.master_cells
        for cell_row in master_cells:
            for cell in cell_row:
                row = cell.row
                col = cell.col
                if __isInActiveRange__(cameras, row, col):
                    if __isInvisibleRange__(cameras, row, col):
                        if cell.cell_state_enum != CellStateEnum.CELL_STATE_INVISIBLE:
                            print("test_Scene_grd - cell within active invisible of a cameras wrong state = ")
                            print(cell.id, row, col)
                            assert False
                    else:
                        if cell.cell_state_enum != CellStateEnum.CELL_STATE_VISIBLE:
                            print("test_Scene_grd - cell within active invisible of a cameras wrong state = ")
                            print(cell.id, row, col)
                            assert False
                else:
                    if cell.cell_state_enum != CellStateEnum.CELL_STATE_INACTIVE:
                        print("test_Scene_grd - cell not within active range of a camera is active")
                        print(cell.id, row, col)
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(2.6) All cells that changed state were transitioned
#(2.7) Cells have correct Active state relative to Camera/Screen/Histeresis
#(2.8) Invisible border ranges are correct
def _testMasterCellsActiveState_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            #may need to make  another inner loop if we have multiple master grids in a scene (for parallax scrolling)
            scene_master_grid = scene._scene_master_grid
            for camera in scene_master_grid._cameras.values():
                __testMasterCellsActiveState__(scene_master_grid,camera)
    except Exception as e:
        print(e)
        return False
    return True

def __testMasterCellsActiveState__(scene_master_grid, camera):
    try:
        camera_position = camera._position
        window_size = camera.window_size
        cell_size = scene_master_grid.cell_size
        activate_range = camera.getActivateRange()
        deactivate_range = camera.getDeactivateRange()
        numb_rows = scene_master_grid.numb_rows
        numb_cols = scene_master_grid.numb_cols
        previous_camera_position = camera.__previous_camera_position__ #This is only checked and updated by this test code
        previous_active_row_range = camera.__previous_active_row_range__ #This is only checked and updated by this test code
        previous_active_col_range = camera.__previous_active_col_range__ #This is only checked and updated by this test code

        #Initialized cameras or size changed cameras don't follow the same rules
        #So rather than test the change from one frame to the next, just verify current position is correct
        #There is not a deactivate histeresis in play for initialized or size changed camera
        if previous_camera_position is None or camera.__has_changed_size__:
            #initialize for the next test, this algorithm checks the change from 1 frame to the next
            camera.__previous_active_row_range__ = list(camera.current_active_row_range)
            camera.__previous_active_col_range__ = list(camera.current_active_col_range)
            camera.__previous_camera_position__ = list(camera._position)
            #This makes sure that where the camera is now (were it first is shown), cells are all active
            __initialCameraState__(scene_master_grid, camera)
            camera.__has_changed_size__ = False
            return

        # "scene_grid.__previous_camera_position__" is the test value only updated here
        # "scene_grid.__previous_active_<col/row>_range__" are test values only updated here
        if camera_position[0] > previous_camera_position[0]:  # moved right
            max_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // cell_size[0]
            # could be further out due to hysteresis
            if max_col < previous_active_col_range[1]:
                max_col = previous_active_col_range[1]
            min_col = (camera_position[0] - deactivate_range[0]) // cell_size[0]
            if min_col < previous_active_col_range[0]:  # wasn't active before we moved
                min_col = previous_active_col_range[0]
        elif camera_position[0] < previous_camera_position[0]:  # moved left
            max_col = (camera_position[0] + window_size[0] + deactivate_range[0] - 1) // cell_size[0]
            if max_col > previous_active_col_range[1]:
                max_col = previous_active_col_range[1]  # wasn't active before we moved
            min_col = (camera_position[0] - activate_range[0]) // cell_size[0]
            if min_col > previous_active_col_range[0]:
                min_col = previous_active_col_range[0]
        else:
            min_col = previous_active_col_range[0]
            max_col = previous_active_col_range[1]

        if camera_position[1] > previous_camera_position[1]:  # moved down
            max_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // cell_size[1]
            if max_row < previous_active_row_range[1]:
                max_row = previous_active_row_range[1]
            min_row = (camera_position[1] - deactivate_range[1]) // cell_size[1]
            if min_row < previous_active_row_range[0]:  # wasn't active before we moved
                min_row = previous_active_row_range[0]
        elif camera_position[1] < previous_camera_position[1]:  # moved up
            max_row = (camera_position[1] + window_size[1] + deactivate_range[1] - 1) // cell_size[1]
            if max_row > previous_active_row_range[1]:
                max_row = previous_active_row_range[1]  # wasn't active before we moved
            min_row = (camera_position[1] - activate_range[1]) // cell_size[1]
            if min_row > previous_active_row_range[0]:
                min_row = previous_active_row_range[0]
        else:
            min_row = previous_active_row_range[0]
            max_row = previous_active_row_range[1]

        #handle the case where the camera hase moved far enough that there are no overlapping rows/columns:
        if camera_position[0] > previous_camera_position[0]:  # moved right
            if camera_position[1] > previous_camera_position[1]:  # moved down
                if min_col > previous_active_col_range[1] or min_row > previous_active_row_range[1]:
                    min_col = (camera_position[0] - activate_range[0]) // cell_size[0]
                    min_row = (camera_position[1] - activate_range[1]) // cell_size[1]
            elif camera_position[1] < previous_camera_position[1]:  # moved up
                if min_col > previous_active_col_range[1] or max_row < previous_active_row_range[0]:
                    min_col = (camera_position[0] - activate_range[0]) // cell_size[0]
                    max_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // cell_size[1]
            else: #just moved right
                if min_col > previous_active_col_range[1]:
                    min_col = (camera_position[0] - activate_range[0]) // cell_size[0]
        elif camera_position[0] < previous_camera_position[0]:  # moved left
            if camera_position[1] > previous_camera_position[1]:  # moved down
                if max_col < previous_active_col_range[0] or min_row > previous_active_row_range[1]:
                    max_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // cell_size[0]
                    min_row = (camera_position[1] - activate_range[1]) // cell_size[1]
            elif camera_position[1] < previous_camera_position[1]:  # moved up
                if max_col < previous_active_col_range[0] or max_row < previous_active_row_range[0]:
                    max_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // cell_size[0]
                    max_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // cell_size[1]
            else: #just moved left
                if max_col < previous_active_col_range[0]:
                    max_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // cell_size[0]
        elif camera_position[1] > previous_camera_position[1]:  # moved down (only)
            if min_row > previous_active_row_range[1]:
                min_row = (camera_position[1] - activate_range[1]) // cell_size[1]
        elif camera_position[1] < previous_camera_position[1]:  # moved up (only)
            if max_row < previous_active_row_range[0]:
                max_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // cell_size[1]

        if min_col < 0:
            min_col = 0
        if max_col >= numb_cols:
            max_col = numb_cols - 1
        if min_row < 0:
            min_row = 0
        if max_row >= numb_rows:
            max_row = numb_rows - 1

        # updated for the next test
        camera.__previous_active_row_range__ = list(camera.current_active_row_range)
        camera.__previous_active_col_range__ = list(camera.current_active_col_range)
        camera.__previous_camera_position__ = list(camera._position)

        # Verify testing algorithm and game engine update algorithm come up with same ranges
        if min_row != camera.current_active_row_range[0]:
            print("test_Scene_grd - test min_row = "
                  + str(min_row)
                  + " but grid current_active_row_range[0] = "
                  + str(camera.current_active_row_range[0]))
            assert False
        if max_row != camera.current_active_row_range[1]:
            print("test_Scene_grd - test max_row = "
                  + str(max_row)
                  + " but grid current_active_row_range[1] = "
                  + str(camera.current_active_row_range[1]))
            assert False
        if min_col != camera.current_active_col_range[0]:
            print("test_Scene_grd - test min_col = "
                  + str(min_col)
                  + " but grid _current_active_col_range[0] = "
                  + str(camera.current_active_col_range[0]))
            assert False
        if max_col != camera.current_active_col_range[1]:
            print("test_Scene_grd - test max_col = "
                  + str(max_col)
                  + " but grid _current_active_col_range[1] = "
                  + str(camera.current_active_col_range[1]))
            assert False
        master_cells = scene_master_grid.master_cells
        for row in range(numb_rows):
            for col in range(numb_cols):
                # check based on the active/inactive algorithm that we correctly activated/deactivated the cells
                current_cell = master_cells[row][col]
                borders = current_cell.borders  # [left, bottom, right, top]
                if (min_row <= row <= max_row) and (min_col <= col <= max_col):
                    expected_cell_enum = __cellExpectedEnum__(scene_master_grid, borders)
                    if current_cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                        print("test_Scene_grid - expected cell state enum of active of some sort")
                        assert False
                    if expected_cell_enum != current_cell.cell_state_enum:
                        print("test_Scene_grid - Test fail due to Unexpected cell state enum.")
                        print("Current cell state: " + str(current_cell.cell_state_enum))
                        print("Expected cell state enum: " + str(expected_cell_enum))
                        print("cell id: " + str(current_cell.cell_id))
                        assert False
                a = camera_position[0] + activate_range[0] + window_size[0] > borders[0]  # left edge
                b = camera_position[0] - activate_range[0] <= borders[2]  # Right edge
                c = camera_position[1] + activate_range[1] + window_size[1] > borders[1]  # bottomedge
                d = camera_position[1] - activate_range[1] <= borders[3]  # Top edge
                if a and b and c and d:  # some part of the cell is on screen, or within hysteresis range
                    if not __masterCellIsActive__(current_cell):
                        print("test_Scene_grid - Cell [" + str(row) + "," + str(col) + "] is within screen range but is inactive")
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

#When the camera is initialized, we do not have the previous test values to use to determine
#the histeresis precisely.  We can verify minimum ranges of active cells however.  Make sure none of them
#Are inactive
def __initialCameraState__(scene_master_grid, camera):
    try:
        camera_position = camera._position
        window_size = camera.window_size
        cell_size = scene_master_grid.cell_size
        activate_range = camera.getActivateRange()
        numb_rows = scene_master_grid.numb_rows
        numb_cols = scene_master_grid.numb_cols

        row_start = (camera_position[1] - activate_range[1]) // cell_size[1]
        if row_start < 0:
            row_start = 0
        row_end = (camera_position[1] + window_size[1] - 1 + activate_range[1]) // cell_size[1]
        if row_end >= numb_rows:
            row_end = numb_rows - 1
        col_start = (camera_position[0] - activate_range[0]) // cell_size[0]
        if col_start < 0:
            col_start = 0
        col_end = (camera_position[0] + window_size[0] - 1 + activate_range[0]) // cell_size[0]
        if col_end >= numb_cols:
            col_end = numb_cols - 1

        #The actual values of the camera
        current_active_col_range = camera.current_active_col_range
        current_active_row_range = camera.current_active_row_range

        #We might have greater ranges than this if the camera was initialized AND moved due to histeresis
        if current_active_col_range[0] > col_start:
            print("Expected col range of initialized camera left error, id: ",camera.camera_id)
            assert False
        if current_active_col_range[1] < col_end:
            print("Expected col range of initialized camera right error, id: ",camera.camera_id)
            assert False
        if current_active_row_range[0] > row_start:
            print("Expected col range of initialized camera top error, id: ",camera.camera_id)
            assert False
        if current_active_row_range[1] < row_end:
            print("Expected col range of initialized camera bottom error, id: ",camera.camera_id)
            assert False

        master_cells = scene_master_grid.master_cells
        for row in range(numb_rows):
            for col in range(numb_cols):
                # check based on the active/inactive algorithm that we correctly activated/deactivated the cells
                current_cell = master_cells[row][col]
                if (row_start <= row <= row_end) and (col_start <= col <= col_end):
                    if current_cell.cell_state_enum == CellStateEnum.CELL_STATE_INACTIVE:
                        print("test_Scene_grid - expected cell state enum of active of some sort")
                        assert False

    except Exception as e:
        print(e)
        assert False


### Helper Functions ###

#Get's the current list of entities, and adds all entities in this cell to it.
#Assert an error if duplicates are found
def __cellGetEntities__(cell, entities):
    try:
        current = cell.head
        while current is not None:
            if current in entities:
                print("test_Scene_grid - duplicate entity found in cell, " + str(cell.cell_id))
                print("entity id: "+ str(current.entity_id))
                assert False
            entities.append(current)
            current = current.next_node
        #now iterate the invisible linked list
        current = cell.invisible_head
        while current is not None:
            if current in entities:
                print("test_Scene_grid - duplicate entity found in invisible nodes, " + str(cell.cell_id))
                print("entity id: "+ str(current.entity_id))
                assert False
            entities.append(current)
            current = current.next_node
        #finally look through ethereal invisibles
        for node in cell.invisible_ethereal_nodes.values():
            if node in entities:
                print("test_Scene_grid - duplicate entity found in invisible_ethereal_nodes, " + str(cell.cell_id))
                print("entity id: "+ str(current.entity_id))
                assert False
            entities.append(node)
        return entities
    except Exception as e:
        print(e)
        assert False

def __masterCellIsActive__(master_cell):
    if master_cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE or \
            master_cell.cell_state_enum == CellStateEnum.CELL_STATE_INVISIBLE:
        return True
    return False

#This function NEVER expects inactive, due to hysteresis variablility.  If this function is checked, it will either
#return active, or some form of invisibility.  If cell expected to be inactive, this function is not called at all
#All cameras must be checked, because any camera that has a cell in range will then make it visible
def __cellExpectedEnum__(scene_master_grid, cell_borders):
    expected_cell_state = CellStateEnum.CELL_STATE_INVISIBLE
    #This funky algorithm checks every camera, and sees if any portion of the cell lies within the visible area
    #if it does, than we return expected value of Active.  If none of them fit this, then we return invisble
    for camera in scene_master_grid._cameras.values():
        camera_position = camera._position
        window_size = camera.window_size
        #If left edge of cell is beyond right edge of the screen
        if camera_position[0] + window_size[0] - 1 < cell_borders[0]:
            pass
        #if top edge of cell is beyond bottom edge of screen
        elif camera_position[1] + window_size[1] - 1 < cell_borders[3]:
            pass
        #if right edge of cell is left of the screen
        elif camera_position[0] > cell_borders[2]:
            pass
        #if bottom edge of cell above top edge of screen
        elif camera_position[1] > cell_borders[1]:
            pass
        else:
            expected_cell_state = CellStateEnum.CELL_STATE_VISIBLE
    return expected_cell_state

#Verify every sprite in the cell is also in the sprite_dict
def __findSpriteInDict__(cell, sprite_dict):
    try:
        current = cell.head
        while current is not None:
            if sprite_dict.get(current.getEntityId()) is None:
                print("Found sprite in grid not in dict, id: " + str(current.getEntityId()))
                assert False
            current = current.next_node
        #next check the invisible linked list
        current = cell.invisible_head
        while current is not None:
            if sprite_dict.get(current.getEntityId()) is None:
                print("Found sprite in invisible nodes not in dict, id: " + str(current.getEntityId()))
                assert False
            current = current.next_node
        #finally check the
        for entity_id, node in cell.invisible_ethereal_nodes.items():
            if sprite_dict.get(node.getEntityId()) is None:
                print("Found sprite in invisible_ethereal_nodes not in dict, id: " + str(current.getEntityId()))
                assert False
            if entity_id != node.getEntityId():
                print("Entity id mismatch in invisible_ethereal_nodes dict, id: " + str(current.getEntityId()))
                assert False
    except Exception as e:
        print(e)
        return False
    return True

#returns true is any of the cameras contains the [row,col]
def __isInActiveRange__(cameras, row, col):
    try:
        for camera in cameras:
            active_row_range = camera.current_active_row_range
            active_col_range = camera.current_active_col_range
            if active_row_range[0] <= row <= active_row_range[1] and \
                    active_col_range[0] <= col <= active_col_range[1]:
                return True
        return False
    except Exception as e:
        print(e)
        assert False

#returns true iff a cell is in invisible range of atleast 1 camera and not in  visible range of any camera
def __isInvisibleRange__(cameras, row, col):
    try:
        invisible = False #Set true if any camera has a cell as invisible
        for camera in cameras:
            active_row_range = camera.current_active_row_range
            active_col_range = camera.current_active_col_range
            invisible_borders = camera.current_invisible_border
            if active_row_range[0] <= row <= active_row_range[1] and \
                    active_col_range[0] <= col <= active_col_range[1]:
                invisible = True #We may be invisible
                #If we pass this than we are actually visible to this camera
                if invisible_borders[TOP] <= row <= invisible_borders[BOTTOM] and \
                        invisible_borders[LEFT] <= col <= invisible_borders[RIGHT]:
                    return False
        return invisible
    except Exception as e:
        print(e)
        assert False
