import random
import os
import sys
from Sprite_state import SpriteStateEnum

from Game_Scene.Test.Test_Suites import test_Scene_layer, test_Scene_grid, test_Scene_cell, test_Scene_node
from Game_Scene.Test.Test_Suites import test_Entity_manager, test_Scene_manager, test_Scene_camera

def _randomFromList(alist):
    index = random.randint(0, len(alist)-1)
    return alist[index]

def _getActiveScenes(game_engine):
    return game_engine._scene_manager._active_scenes

def _sceneHasVisibleSprite(scene):
    for sprite in scene._sprites.values():
        if _spriteIsVisible(sprite):
            return True
    return False

def _spriteIsVisible(sprite):
    sprite_enum = sprite.current_sprite_state.sprite_state_enum
    if sprite_enum == SpriteStateEnum.SPRITE_STATE_ACTIVE or \
            sprite_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE or \
            sprite_enum == SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL or \
            sprite_enum == SpriteStateEnum.SPRITE_STATE_ACTIVE_ETHEREAL:
        #If the render height is <=0, the image has a Z offset and is off the map
        if sprite.image_render_coordinates[3] > 0:
            return True
    return False

#Pass in a scene which has at least 1 visible sprite, get back a random sprite selction
def _getVisibleSpriteIdFromScene(scene):
    candidate_ids = list()
    for entity_id, sprite in scene._sprites.items():
        if _spriteIsVisible(sprite):
            candidate_ids.append(entity_id)
    sprite_id = _randomFromList(candidate_ids)
    return sprite_id

############################################################################################################

#TODO - test by changing clone coords
#TODO - test the negative coord render case


#tests obj 4.1, changing the width/height of the image_render_coordinates for the parent sprite
    # (4.1) Sprite Render Coordinates fully covered
def chaos_testSpriteRenderCoordinates_41parent(game_engine, args = None):
    #-1 signifies a NOP - when script was run no qualifying params existed to test
    if args is not None and args[0] == -1:
        return [-1], True

    is_passing = True
    active_scenes = _getActiveScenes(game_engine)
    candidate_scenes = list()#list of ID's (not needed if args are specified)

    #If args is None, that means randomly generate the params
    if args is None:
        #look through active scenes for ones that have at least 1 visible sprite
        for scene_id, scene in active_scenes.items():
            if _sceneHasVisibleSprite(scene):
                candidate_scenes.append(scene_id)
        #like a NOP, nothing to test here
        if len(candidate_scenes) == 0:
            return [-1], True

    #When generating the random vals, we will use this to store the return args
    param_list = [0,0,0]
    #index 0 = scene_41_id
    #index 1 = sprite_41_id
    #index 2 = sprite_41_change : [ 0: original_x,
    #                               1: changed_x1, 2: changed_x2,
    #                               3: original_y,
    #                               4: changed_y1, 5: changed_y2,
    #                               6: original_width,
    #                               7: changed_width1, 8: changed_width2,
    #                               9: original_height,
    #                               10: changed_height1, 11: changed_height2]

    if args is None:
        scene_41_id = _randomFromList(candidate_scenes)
        param_list[0] = scene_41_id
        sprite_41_id = _getVisibleSpriteIdFromScene(active_scenes[scene_41_id])
        param_list[1] = sprite_41_id
    else:
        scene_41_id = args[0]
        sprite_41_id = args[1]
    scene_41 = active_scenes[scene_41_id]
    sprite_41 = scene_41._sprites[sprite_41_id]

    if args is None:
        sprite_41_image_x = sprite_41.image_render_coordinates[0]
        sprite_41_changed_x1 =sprite_41_image_x-1
        sprite_41_changed_x2 =sprite_41_image_x+1
        sprite_41_image_y = sprite_41.image_render_coordinates[1]
        sprite_41_changed_y1 =sprite_41_image_y-1
        sprite_41_changed_y2 =sprite_41_image_y+1
        sprite_41_image_width = sprite_41.image_render_coordinates[2]
        sprite_41_changed_width1 =sprite_41_image_width-1
        sprite_41_changed_width2 =sprite_41_image_width+1
        sprite_41_image_height = sprite_41.image_render_coordinates[3]
        sprite_41_changed_height1 =sprite_41_image_height-1
        sprite_41_changed_height2 =sprite_41_image_height+1
        sprite_41_change = [sprite_41_image_x, sprite_41_changed_x1, sprite_41_changed_x2,
                            sprite_41_image_y, sprite_41_changed_y1, sprite_41_changed_y2,
                            sprite_41_image_width, sprite_41_changed_width1, sprite_41_changed_width2,
                            sprite_41_image_height, sprite_41_changed_height1, sprite_41_changed_height2]
    else:
        sprite_41_change = args[2]

    param_list[2] = sprite_41_change

    #We don't want to see the printed errors for all of the chaos tests
    STDOUT = sys.stdout
    f = open(os.devnull, 'w')
    testSpriteRenderCoordinates = test_Scene_node._testSpriteRenderCoordinates_
    #Run the test 8 times, once for each render_coordinate change
    for trial in range(8):
        sys.stdout = f
        #reset the original values
        sprite_41.image_render_coordinates[0] = sprite_41_change[0]
        sprite_41.image_render_coordinates[1] = sprite_41_change[3]
        sprite_41.image_render_coordinates[2] = sprite_41_change[6]
        sprite_41.image_render_coordinates[3] = sprite_41_change[9]
        # change the X value
        if trial == 0:
            sprite_41.image_render_coordinates[0] = sprite_41_change[1]
        elif trial == 1:
            sprite_41.image_render_coordinates[0] = sprite_41_change[2]
        # change the Y value
        elif trial == 2:
            sprite_41.image_render_coordinates[1] = sprite_41_change[4]
        elif trial == 3:
            sprite_41.image_render_coordinates[1] = sprite_41_change[5]
        # change the width
        elif trial == 4:
            sprite_41.image_render_coordinates[2] = sprite_41_change[7]
        elif trial == 5:
            sprite_41.image_render_coordinates[2] = sprite_41_change[8]
        # change the height
        elif trial == 6:
            sprite_41.image_render_coordinates[3] = sprite_41_change[10]
        elif trial == 7:
            sprite_41.image_render_coordinates[3] = sprite_41_change[11]

        #We should NOT pass the test, if we do, we missed the error
        if testSpriteRenderCoordinates(game_engine):
            sys.stdout = STDOUT
            print("chaos_testSpriteRenderCoordinates_41parent Failed trial: ", trial)
            print("Scene Id:",scene_41_id)
            print("Sprite Id:",sprite_41_id)
            print("Change params: ", sprite_41_change)
            is_passing = False

    #restore the sprite back to correct state
    sprite_41.image_render_coordinates[0] = sprite_41_change[0]
    sprite_41.image_render_coordinates[1] = sprite_41_change[3]
    sprite_41.image_render_coordinates[2] = sprite_41_change[6]
    sprite_41.image_render_coordinates[3] = sprite_41_change[9]

    sys.stdout = STDOUT
    f.close()
    return param_list, is_passing


#CHAOS_TEST_GROUPS names must match CHAOS_TESTS names
#CHAOS_TEST_GROUPS is for first time runs, CHAOS_TESTS is for loading saved runs

#Define each test here by name
CHAOS_TESTS = dict()
CHAOS_TESTS["chaos_testSpriteRenderCoordinates_41parent"] = chaos_testSpriteRenderCoordinates_41parent

#Define a group of chaos_tests based on the original test here
CHAOS_TEST_GROUPS = dict()
CHAOS_TEST_GROUPS["_testSpriteRenderCoordinates_"] = \
    {"chaos_testSpriteRenderCoordinates_41parent": chaos_testSpriteRenderCoordinates_41parent,}