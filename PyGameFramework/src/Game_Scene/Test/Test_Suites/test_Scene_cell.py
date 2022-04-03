from Sprite_state import SpriteStateEnum
from Game_Scene.Scene_Cell.Scene_cell import CellStateEnum
from Game_Scene.Test.Test_Suites.test_Scene_functions import _getNodeByEntityIdInCell_
#In the cell.borders list, the borders are indexed as such (WHO CHOSE THAT?!?)
LEFT_BORDER = 0
BOTTOM_BORDER = 1
RIGHT_BORDER = 2
TOP_BORDER = 3

#(3.14) All layers in a scene have equivalent cell_states
#(3.15) scene_cell's grid reference is correct
#(3.16) scene_cell's scene_layer reference is correct
#(3.17) master_grid has 1 scene_grid ref per layer
#(3.18) master_grid references the correct scene_grids
#(3.19) master_cells reference the correct master_grid
def _testSceneCellReferences_(game_engine_mock):
    try:
        for scene_id, scene in game_engine_mock._scene_manager._scenes.items():
            master_grid = scene._scene_master_grid
            numb_cell_rows = master_grid.numb_rows
            numb_cell_cols = master_grid.numb_cols
            master_cells = master_grid.master_cells
            for row in range(0, numb_cell_rows):
                for col in range(0, numb_cell_cols):
                    if master_cells[row][col].master_grid is not master_grid: #(3.19)
                        print("test Scene_cell - master cell master grid ref mismatch")
                        assert False
            numb_scene_layers = len(scene._scene_layers)
            if len(master_grid._scene_grids) != numb_scene_layers: #(3.17)
                print("test Scene_cell - numb layers and numb grids mismatch")
                assert False
            for layer_id, scene_layer in scene._scene_layers.items():
                if master_grid._scene_grids[layer_id] is not scene_layer.scene_grid: #(3.18)
                    print("test Scene_cell - scene grid ref mismatch")
                    assert False
                scene_grid = scene_layer.scene_grid
                scene_cells = scene_grid._scene_cells
                for row in range(0, numb_cell_rows):
                    for col in range(0, numb_cell_cols):
                        cell = scene_cells[row][col]
                        if cell.grid is not scene_grid: #(3.15)
                            print("test Scene_cell - cell grid ref mismatch")
                            assert False
                        if cell.scene_layer is not scene_layer: #(3.16)
                            print("test Scene_cell - cell layer ref mismatch")
                            assert False
                        if cell.cell_state_enum != master_cells[row][col].cell_state_enum: #(3.14)
                            print("test Scene_cell - cell state mismatch")
                            assert False
    except Exception as e:
        print(e)
        return False
    return True

#(3.1) Cells are sorted
#(3.2) Invisible sprites are not in the Linked List of Nodes
#(3.3) Cell contains reference to correct grid
#(3.4) Cell contains reference to correct scene layer
#(3.5) Cell state enum matches current cell state
#(3.6) No inactive sprites in a cell
#(3.7) No AlwaysActiveInvisible Sprites in cells
#(3.8) No duplicate entity_ids within a cell
def _testCellsAreSorted_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            for scene_layer in scene._scene_layers.values():
                __testCellsAreSorted__(scene_layer)
    except Exception as e:
        print(e)
        return False
    return True

def __testCellsAreSorted__(scene_layer):
    try:
        scene_grid = scene_layer.scene_grid
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                if cell.previous_cell_state_enum != cell.cell_state_enum:
                    print("Previous and current cell state mismatch (wasn't transitioned), id: " + str(cell.cell_id))
                    assert False
                if cell.scene_layer != scene_layer:
                    print("test Scene_cell - scene layer ref incorrect") #(65)
                    assert False
                if cell.grid != scene_grid:
                    print("test Scene_cell - grid ref incorrect") #(64)
                    assert False
                #Invisible and inactive cells are not sorted, only check active
                check_sorted = False
                if cell.cell_state_enum == CellStateEnum.CELL_STATE_VISIBLE:
                    check_sorted = True
                if not __cellIsSorted__(cell, check_sorted):
                    print("cell not sorted, cell id: " + str(cell.cell_id))
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(3.9) Visible sprites are not in the invisible sprites list
#(3.10) Invisible active sprites are in the correct cells
#(3.11) Invisible sprite cell ref consistent with cell
def _testInvisibleSpritesLists_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            for scene_layer in scene._scene_layers.values():
                __testInvisibleEtherealSpritesLists__(scene_layer)
                __testInvisibleTangibleSpritesLists__(scene_layer)
            sprites = scene._sprites
            for entity_id, sprite in sprites.items():
                if sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE:
                    cell = sprite.cell
                    if cell is None:
                        print("test Scene_cell - invisible_tangible sprite cell is None, id: " + str(entity_id))
                        assert False
                    if _getNodeByEntityIdInCell_(entity_id, cell, invisible=True) is None:
                        print("test Scene_cell - invisible_tangible sprite ref wrong cell, id: " + str(entity_id))
                        assert False
                    if not __spriteWorldPositionInCell__(sprite, cell.borders):
                        print("test Scene_cell - invisible sprite ref cell outside of border, id: " + str(entity_id))
                        assert False
                elif sprite.getSpriteStateEnum() == SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL:
                    cell = sprite.cell
                    if cell is None:
                        print("test Scene_cell - invisible_ethereal sprite cell is None, id: " + str(entity_id))
                        assert False
                    if cell.invisible_ethereal_nodes.get(entity_id) is None:
                        print("test Scene_cell - invisible_ethereal sprite ref wrong cell, id: " + str(entity_id))
                        assert False
                    if not __spriteWorldPositionInCell__(sprite, cell.borders):
                        print("test Scene_cell - invisible sprite ref cell outside of border, id: " + str(entity_id))
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

def __testInvisibleEtherealSpritesLists__(scene_layer):
    try:
        scene_grid = scene_layer.scene_grid
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                for entity_id, sprite in cell.invisible_ethereal_nodes.items():
                    if sprite.isVisible():
                        print("test Scene_cell - visible sprite in invisible list, id: " + str(entity_id))
                        assert False
                    if not sprite.isEthereal():
                        print("test Scene_cell - tangible sprite in invisible_ethereal list, id: " + str(entity_id))
                        assert False
                    if not __spriteWorldPositionInCell__(sprite, cell.borders):
                        print("test Scene_cell - invisible sprite in wrong cell, id: " + str(entity_id))
                        assert False
                    if sprite.cell != cell: #90
                        print("test Scene_cell - sprite cell ref doesn't match cell, id: " + str(entity_id))
                        assert False
    except Exception as e:
        print(e)
        assert False
    return True

def __testInvisibleTangibleSpritesLists__(scene_layer):
    try:
        scene_grid = scene_layer.scene_grid
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                sprite = cell.invisible_head
                while sprite is not None:
                    if sprite.isVisible():
                        print("test Scene_cell - visible sprite in invisible_tangible list, id: " + str(sprite.entity_id))
                        assert False
                    if sprite.isEthereal():
                        print("test Scene_cell - ethereal sprite in invisible_tangible list, id: " + str(sprite.entity_id))
                        assert False
                    if not __spriteWorldPositionInCell__(sprite, cell.borders):
                        print("test Scene_cell - invisible sprite in wrong cell, id: " + str(sprite.entity_id))
                        assert False
                    if sprite.cell != cell: #90
                        print("test Scene_cell - sprite cell ref doesn't match cell, id: " + str(sprite.entity_id))
                        assert False
                    sprite = sprite.next_node
    except Exception as e:
        print(e)
        assert False
    return True

#(3.20) Link List is consistent
#eg node.next.previous = node
def _testLinkedListsAreConsistent_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._scenes.values():
            for scene_layer in scene._scene_layers.values():
                __testLinkedListsAreConsistent__(scene_layer)
    except Exception as e:
        print(e)
        assert False
    return True

def __testLinkedListsAreConsistent__(scene_layer):
    try:
        scene_grid = scene_layer.scene_grid
        for cell_row in scene_grid._scene_cells:
            for cell in cell_row:
                if not __linkedListIsConsistent__(cell):
                    print('Cell has a LL inconsistency: ' + str(cell.cell_id))
                    assert False
    except Exception as e:
        print(e)
        assert False
    return True

#(3.12) Sprite/Clone World Position always resides in current cell
#(3.13) All sprites/clones in visible cells are contained in cell
def _testSpritesStayInBorders_(game_engine_mock):
    try:
        for scene in game_engine_mock._scene_manager._active_scenes.values():
            for scene_layer in scene._scene_layers.values():
                __testSpritesStayInBorders__(scene_layer)
    except Exception as e:
        print(e)
        assert False
    return True

def __testSpritesStayInBorders__(scene_layer):
    try:
        cell_grid = scene_layer.scene_grid._scene_cells
        for cell_row in cell_grid:
            for cell in cell_row:
                #We will iterate through first the visible linked list, then the invisible linked list
                current_node = cell.head
                visible_done = False
                if current_node is None: #if there are no visible nodes
                    current_node = cell.invisible_head
                    visible_done = True
                borders = cell.borders
                while current_node is not None:
                    #Both Tangible sprites (for their bounding boxed) and visible sprites (for image) must be contained in a cell
                    if current_node.isVisible() or (not current_node.isEthereal()):
                        if not __spriteWithinBorders__(current_node, borders):
                            print("test Scene_cell - sprite/clone crosses cell border, id: "+ str(current_node.entity_id))
                            assert False
                    current_node = current_node.next_node
                    if current_node is None and not visible_done:
                        visible_done = True
                        current_node = cell.invisible_head
    except Exception as e:
        print(e)
        assert False
    return True

### Helper Functions ###

def __spriteWithinBorders__(sprite, borders):
    image_width = sprite.image_render_coordinates[2]
    image_height = sprite.image_render_coordinates[3]
    world_position = sprite.world_position
    if world_position[0] < borders[LEFT_BORDER]:
        print("World position 0 < left border")
        return False
    if world_position[0] > borders[RIGHT_BORDER]:
        print("World position 0 crossed right border")
        return False
    if world_position[0] + image_width - 1 > borders[RIGHT_BORDER]:
        print("Image crossed right border")
        return False
    if world_position[1] < 0:
        if borders[TOP_BORDER] != 0:
            print("World position 1 negative and top border != 0")
            return False
    elif world_position[1] < borders[TOP_BORDER]:
        print("World position 1 < top border")
        return False
    if world_position[1] > borders[BOTTOM_BORDER]:
        print("World position 1 crossed bottom border bottom border")
        return False
    if world_position[1] + image_height - 1 > borders[BOTTOM_BORDER]:
        print("Image crossed bottom border")
        return False
    return True

#just check the WP origin is within the cell
def __spriteWorldPositionInCell__(sprite, borders):
    world_position = sprite.world_position
    if world_position[0] < borders[LEFT_BORDER]:
        print("World position 0 < left border")
        return False
    if world_position[0] > borders[RIGHT_BORDER]:
        print("World position 0 crossed right border")
        return False
    if world_position[1] < 0:
        if borders[TOP_BORDER] != 0:
            print("World position 1 negative and top border != 0")
            return False
    elif world_position[1] < borders[TOP_BORDER]:
        print("World position 1 < top border")
        return False
    if world_position[1] > borders[BOTTOM_BORDER]:
        print("World position 1 crossed bottom border")
        return False
    return True

def __linkedListIsConsistent__(cell):
    try:
        if cell.head is None:
            return True
        #go forwards
        current_node = cell.head
        next_node = current_node.next_node
        if current_node.previous_node is not None:
            print("Head node has a previous node")
            assert False
        watchdog_count = 0
        while next_node is not None:
            if next_node.previous_node is not current_node:
                print("next_node.previous_node is not current_node")
                assert False
            current_node = next_node
            next_node = current_node.next_node
            watchdog_count += 1
            if watchdog_count > 500000:
                print('__linkedListIsConsistent__: We seem to have a Linked List loop, or more than 500000 items in a cell!')
                assert False
        if current_node is not cell.tail:
            print("final node is not tail")
            assert False
        #go backwards
        current_node = cell.tail
        previous_node = current_node.previous_node
        if current_node.next_node is not None:
            print("tail node has a next node")
            assert False
        watchdog_count = 0
        while previous_node is not None:
            if previous_node.next_node is not current_node:
                print("previous_node.next_node is not current_node")
                assert False
            current_node = previous_node
            previous_node = current_node.previous_node
            if watchdog_count > 500000:
                print('__linkedListIsConsistent__: We seem to have a Linked List loop, or more than 500000 items in a cell!')
                assert False
        if current_node is not cell.head:
            print("final node is not head")
            assert False
    except Exception as e:
        print(e)
        return False
    return True

def __cellIsSorted__(cell, check_sorted):
    try:
        if cell.head is None:
            if cell.tail is not None:  # both or neither should be none
                print ("If cell.head is None, cell.tail must also be None (empty Linked List)")
                assert False
            return True  # nothing to check, cell is empty
        current_node = cell.head
        next_node = current_node.next_node
        watchdog_count = 0
        while True:
            if not current_node.isActivated():
                print("Inactive node found in a cell, id: " + str(current_node.entity_id))
                assert False
            if (not current_node.isVisible()) and current_node.isEthereal():
                print("test_Scene_cell __testIsSorted__, Invisible Ethereal Node in Linked List " + str(
                    current_node.entity_id))
                assert False
            try:
                sprite_state_enum = current_node.getSpriteStateEnum()
                if sprite_state_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL:
                    print("test_Scene_cell __testIsSorted__, AAInvisibleEthereal sprite in a cell, id: " + str(current_node.entity_id))
                    assert False
            except:
                pass #clones do not have sprite state enums
            if next_node is None:
                return True  # we made it with no conflicts
            #we only check the visible cells for sortedness
            if check_sorted:
                if current_node.getGroundPosition()[1] > next_node.getGroundPosition()[1]:
                    print('__testIsSorted__: Incorrectly Sorted!')
                    assert False
            if not cell.residesInCell(current_node.getWorldPosition()):
                print('__testIsSorted__: In Wrong Cell!')
                assert False
            current_node = next_node
            next_node = current_node.next_node
            watchdog_count += 1
            if watchdog_count > 500000:
                print('__testIsSorted__: We seem to have a Linked List loop, or more than 500000 items in a cell!')
                assert False
    except Exception as e:
        print(e)
        return False
