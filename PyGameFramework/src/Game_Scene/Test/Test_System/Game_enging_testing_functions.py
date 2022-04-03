#Called from Game_engine_testing_system.py

import random
from Game_Scene.Test.Test_System.Rendering_test_parameters import *


def stringListToIntList(alist):
    index = 0
    for string in alist:
        alist[index] = int(string)
        index+=1
    return alist

#When moving or panning randomnly, may want to only move horizontal or vertical
#this function randomly returns a direction
def randomDirection():
    val = random.randint(1,4)
    if val == 1:
        return "horizontal"
    elif val == 2:
        return "vertical"
    elif val == 3:
        return "zshift"
    else:
        return "diagonal"

def isValidChoice(key = 'unknown', choice = None):
    if choice is None:
        print("isValidChoice() choice is None")
        assert(1==2)
    try:
        if key == 'int_any':
            if type(choice) is int:
                return True
        elif key == 'int_1+':
            if type(choice) is int:
                if choice > 0:
                    return True
        elif key == 'x,y': #need a list of 2 ints
            if type(choice) is list \
                    and len(choice) == 2 \
                    and type(choice[0]) is int \
                    and type(choice[1]) is int:
                return True
        elif key == 'x,y,z': #need a list of 3 ints
            if type(choice) is list \
                    and len(choice) == 3 \
                    and type(choice[0]) is int \
                    and type(choice[1]) is int \
                    and type(choice[2]) is int:
                return True
        elif key == 'unknown':
            print("isValidChoice() invalid key: " + str(key))
            assert(1==2)
        return False
    except:
        return False

'''
Simulate the next call to render
'''
def update(game_engine_mock, update_count = 0):
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('*** Update ' + str(update_count) + ' ***')
    game_engine_mock.update()

'''
Create a new sprite and add it to the grid - creates the behavior state and particle and links it
'''
def insertSprite(game_engine_mock,
                 scene_id = -1, #-1 for random
                 layer_id = -1,
                 position = None,
                 resource_id = 0,
                 active = True,
                 physics_active = True,
                 behavior_active = True,
                 ai_active = True,
                 visible = True,
                 ethereal = False,
                 always_active = True):
    if scene_id == 0:
        return 0, [0]  # Treat as NOP
    #manual inputs
    if scene_id is None:
        position = input("position: <#,#,#>\n>>>")
        position = position.split(',')
        position = stringListToIntList(position)
        resource_id = int(input("resource_id: <#>\n>>>"))

    #Set random inputs (else we take the scripted passed in inputs)
    elif scene_id == -1:
        current_scenes = game_engine_mock.getSceneIds()
        if len(current_scenes) == 0:
            return 0, [0] #Treat as NOP
        scene_id_index = random.randint(0, len(current_scenes)-1)
        scene_id = current_scenes[scene_id_index]
        current_layers = game_engine_mock.getLayerIds(scene_id)
        if len(current_layers) == 0:
            return 0, [0] #Treat as NOP
        layer_id_index = random.randint(0, len(current_layers)-1)
        layer_id = current_layers[layer_id_index]
        world_size = game_engine_mock.getSceneWorldSize(scene_id)
        #negative values aren't actually legal but we will excersize the error checking for the, as well
        position = [0,0,0]
        position[0] = random.randint(-10, world_size[0] - 1)
        position[1] = random.randint(-10, world_size[1] - 1)
        resource_id = random.randint(GRID_RESOURCE_ID_MIN, GRID_RESOURCE_ID_MIN)
        #Spawn some entities with a Z offset as well - it's for the birds!
        if random.randint(0,10) > 8:
            position[2] = random.randint(-10, 100)
        #Random state params
        if random.randint(0,1) > 0:
            active = True
        else:
            active = False
        if random.randint(0,1) > 0:
            physics_active = True
        else:
            physics_active = False
        if random.randint(0,1) > 0:
            behavior_active = True
        else:
            behavior_active = False
        if random.randint(0,1) > 0:
            ai_active = True
        else:
            ai_active = False
        if random.randint(0,1) > 0:
            visible = True
        else:
            visible = False
        if random.randint(0,1) > 0:
            ethereal = True
        else:
            ethereal = False
        if random.randint(0,1) > 0:
            always_active = True
        else:
            always_active = False
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Insert sprite - ",
              "scene_id: ", scene_id,
              "| layer_id: ",layer_id,
              "| position: ", position,
              "| resource_id: ", resource_id,
              "| active: ", active,
              "| physics_active: ", physics_active,
              "| behavior_active: ", behavior_active,
              "| ai_active: ", ai_active,
              "| visible: ", visible,
              "| ethereal: ", ethereal,
              "| always_active: ", always_active)
    entity_id = game_engine_mock.spawnEntity(scene_id,
                                             layer_id,
                                             position,
                                             resource_id,
                                             active,
                                             physics_active,
                                             behavior_active,
                                             ai_active,
                                             visible,
                                             ethereal,
                                             always_active)
    return entity_id, [scene_id, layer_id, position, resource_id, active, physics_active,
            behavior_active, ai_active, visible, ethereal, always_active]

'''
Completely take sprite out of grid
This may actually just recycle into a sprite "pool"
'''
def removeSprite(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0: #NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Remove sprite: ",entity_id)
    game_engine_mock.removeNode(entity_id) #scripted
    return [entity_id]

'''
These would be external calls to activate or deactivate sprite
The Grid must handle this internally when sprites are off camera
'''
def activateEntity(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Activate Entity: ', entity_id)
    game_engine_mock.activateEntity(entity_id) #scripted
    return [entity_id]

def deactivateEntity(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Deactivate Entity: ', entity_id)
    game_engine_mock.deactivateEntity(entity_id) #scripted
    return [entity_id]

def setEntityAlwaysActive(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Set AA: ', entity_id)
    game_engine_mock.setEntityAlwaysActive(entity_id)
    return [entity_id]

def activateEntityPhysics(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Activate Physics: ', entity_id)
    game_engine_mock.activateEntityPhysics(entity_id)
    return [entity_id]

def activateEntityBehavior(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Activate Behavior: ', entity_id)
    game_engine_mock.activateEntityBehavior(entity_id)
    return [entity_id]

def activateEntityAi(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Activate entity: ', entity_id)
    game_engine_mock.activateEntityAi(entity_id)
    return [entity_id]

def removeEntityAlwaysActive(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Remove AA: ', entity_id)
    game_engine_mock.removeEntityAlwaysActive(entity_id)
    return [entity_id]

def setSpriteInvisible(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Set Invisible: ', entity_id)
    game_engine_mock.setSpriteInvisible(entity_id)
    return [entity_id]

def setEntitySpriteVisible(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Set Visible: ', entity_id)
    game_engine_mock.setEntitySpriteVisible(entity_id)
    return [entity_id]

def setSpriteEthereal(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Set Ethereal: ', entity_id)
    game_engine_mock.setSpriteEthereal(entity_id)
    return [entity_id]

def setSpriteTangible(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Set Tangible: ', entity_id)
    game_engine_mock.setSpriteTangible(entity_id)
    return [entity_id]

def deactivateEntityPhysics(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Deactivate physics: ', entity_id)
    game_engine_mock.deactivateEntityPhysics(entity_id)
    return [entity_id]

def deactivateEntityBehavior(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Deactivate Behavior: ', entity_id)
    game_engine_mock.deactivateEntityBehavior(entity_id)
    return [entity_id]

def deactivateEntityAI(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Deactivate AI: ', entity_id)
    game_engine_mock.deactivateEntityAI(entity_id)
    return [entity_id]

#This function will protect against illegally adding an entity dependancy
#if there are no possible changes, return 0 as the entity_id/dependant_entity_id
#A 0 will be saved to the script.  Since 0 is not a valid entity_id, we will take 0 as a NOP
def addEntityDependancy(game_engine_mock, entity_id = None, dependant_entity_id = None, ):
    #0 is a NOP
    if entity_id == 0:
        return [0, 0]
    current_entities = game_engine_mock.getAllTestingEntityIds()
    current_sprites = game_engine_mock.getAllSprites()
    # We need atleast 2 current entities available to proceed
    if len(current_entities) < 2:
        if GRID_DEBUG_PRINT_FUNCTIONS:
            print("There are less than 2 entities so no dependants can be added")
        return [0, 0]
    # manual call - user enters entity id and dependant id
    #choices will be verified to be valid before taking action
    if entity_id is None:
        entity_id = [0] #set as a list arbitrarily, it will fail the validChoice function
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
        dependant_entity_id = [0]
        while not isValidChoice('int_1+', dependant_entity_id):
            dependant_entity_id = int(input("dependant_entity_id: <#>\n>>>"))
        if not entity_id in current_entities:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("Chosen entity_id does not exist")
            return [0, 0]
        if not dependant_entity_id in current_entities:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("Chosen dependant_entity_id does not exist")
            return [0, 0]
            # can only add this sprite as dependant if it has no dependants itself
        if len(current_sprites[dependant_entity_id].dependant_sprite_nodes) != 0 or \
                len(current_sprites[dependant_entity_id].inactive_dependants) != 0:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("The dependant entity choice is invalid, no action taken")
            return [0, 0]  # 0 is equivalent to a NOP for this function
        if entity_id == dependant_entity_id:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("The dependant entity and master entity cannot be the same, no action taken")
            return [0, 0]
    #-1 selects random entity_ids
    #you cannot add an entity as a dependant, if it has a dependant
    #you cannot add a dependant if it already exists as a dependant for that master
    #the master and dependant cannot be the same id
    elif entity_id == -1:
        #will check each existing entity to see if it has 0 dependants, and add as a dependant_candidate if true
        candidate_dependant_entities = list()
        for current_entity in current_entities:
            sprite = current_sprites[current_entity]
            #if this sprite has no dependants, it can be added as a dependant
            if len(sprite.dependant_sprite_nodes) == 0 and len(sprite.inactive_dependants) == 0:
                candidate_dependant_entities.append(current_entity)
        #when we choose a dependant, need to see if this is already on the master's list
        entity_master_candidates = list(current_entities) #create a COPY of the list
        #we need to search for a legal entity/dependant entity pairing
        keep_going = True
        while keep_going:
            # cannot add a dependant, return 0 to save this action as a NOP
            if len(candidate_dependant_entities) == 0:
                return [0, 0]
            #no remaining possible master candidates
            if len(entity_master_candidates) == 0:
                return [0, 0]
            chosen_dependant_index = random.randint(0, len(candidate_dependant_entities)-1)
            chosen_dependant_id = candidate_dependant_entities[chosen_dependant_index]
            #remove this from the list, for the next loop
            candidate_dependant_entities.remove(chosen_dependant_id)
            #keep trying random master entities until we either run out or find a legal pair
            remaining_master_candidates = list(entity_master_candidates) #create a COPY
            #keep checking masters until we find a legal master/dependant pair
            while len(remaining_master_candidates) > 0 and keep_going:
                master_candidate_index = random.randint(0, len(remaining_master_candidates)-1)
                master_candidate_id = remaining_master_candidates[master_candidate_index]
                remaining_master_candidates.remove(master_candidate_id)
                #master/dependant can't be the same, and master can't already have the dependant
                if master_candidate_id != chosen_dependant_id:
                    #dependants MUST be in the same layer
                    if current_sprites[master_candidate_id].layer is not None and \
                            current_sprites[chosen_dependant_id].layer is not None and \
                            current_sprites[master_candidate_id].layer is current_sprites[chosen_dependant_id].layer:
                        #the master doesn't have this dependant yet
                        if current_sprites[master_candidate_id].dependant_sprite_nodes.get(chosen_dependant_id) is None and \
                                current_sprites[master_candidate_id].inactive_dependants.get(chosen_dependant_id) is None:
                            #we found a match!  overwrite the entity_id and dependant_entity_id with selected values
                            keep_going = False
                            entity_id = master_candidate_id
                            dependant_entity_id = chosen_dependant_id
        #If entity_id is still -1, then there are no possible additions to make
        if entity_id == -1:
            return [0, 0]
    #passed in a value for entity id, try to find a a dependant for it
    elif dependant_entity_id is None:
        try:
            candidate_dependant_entities = list()
            for current_entity in current_entities:
                sprite = current_sprites[current_entity]
                if len(sprite.dependant_sprite_nodes) == 0 and len(sprite.inactive_dependants) == 0:
                    candidate_dependant_entities.append(current_entity)
            keep_going = True
            while keep_going:
                # cannot add a dependant, return 0 to save this action as a NOP
                if len(candidate_dependant_entities) == 0:
                    return [0, 0]
                chosen_dependant_index = random.randint(0, len(candidate_dependant_entities) - 1)
                chosen_dependant_id = candidate_dependant_entities[chosen_dependant_index]
                # remove this from the list, for the next loop
                candidate_dependant_entities.remove(chosen_dependant_id)
                if entity_id != chosen_dependant_id:
                    #dependants MUST be in the same layer
                    if current_sprites[entity_id].layer is not None and \
                            current_sprites[chosen_dependant_id].layer is not None and \
                            current_sprites[entity_id].layer is current_sprites[chosen_dependant_id].layer:
                        #the master doesn't have this dependant yet
                        if current_sprites[entity_id].dependant_sprite_nodes.get(chosen_dependant_id) is None and \
                                current_sprites[entity_id].inactive_dependants.get(chosen_dependant_id) is None:
                            #we found a match!  overwrite the entity_id and dependant_entity_id with selected values
                            keep_going = False
                            dependant_entity_id = chosen_dependant_id
        except Exception as e:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("Exception caught trying to add a dependant")
                print(e)
            return [0, 0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('add to entity: ' + str(entity_id) + ", dependant: " + str(dependant_entity_id))
    #If we get to this call, we should have a valid action
    game_engine_mock.addEntityDependancy(entity_id, dependant_entity_id)
    return [entity_id, dependant_entity_id]

#Check that an entity dependancy exists before removing it.
def removeEntityDependancy(game_engine_mock, entity_id = None, dependant_entity_id = None):
    #0 is NOP for this function.  Saved to script as 0 if no possible actions
    if entity_id == 0:
        return [0,0]
    current_entities = game_engine_mock.getAllTestingEntityIds()
    current_sprites = game_engine_mock.getAllSprites()
    # We need atleast 2 current entities available to proceed
    if len(current_entities) < 2:
        if GRID_DEBUG_PRINT_FUNCTIONS:
            print("There are less than 2 entities so no dependants can be added")
        return [0, 0]
    # manual call
    if entity_id is None:
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
        dependant_entity_id = [0]
        while not isValidChoice('int_1+', dependant_entity_id):
            dependant_entity_id = int(input("dependant_entity_id: <#>\n>>>"))
        if not entity_id in current_entities:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("Chosen entity_id does not exist")
            return [0, 0]
        if not dependant_entity_id in current_entities:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("Chosen dependant_entity_id does not exist")
            return [0, 0]
        if entity_id == dependant_entity_id:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("The dependant entity and master entity cannot be the same, no action taken")
            return [0, 0]
    #-1 is for random choice
    elif entity_id == -1:
        #look through current entities, add all that have dependants as a candidate
        candidate_master_entities = list()
        for entity_id, sprite in current_sprites.items():
            #If we have atleast 1 dependant, we can remove a dependant from this entity
            if len(sprite.dependant_sprite_nodes) > 0 or len(sprite.inactive_dependants) > 0:
                candidate_master_entities.append(entity_id)
        #if no candidates, return the NOP
        if len(candidate_master_entities) == 0:
            return [0,0]
        master_index = random.randint(0, len(candidate_master_entities)-1)
        entity_id = candidate_master_entities[master_index]
        candidate_dependant_entities = list()
        #the key is the dependant_entity_id
        if len(current_sprites[entity_id].dependant_sprite_nodes) > 0:
            for key in current_sprites[entity_id].dependant_sprite_nodes.keys():
                candidate_dependant_entities.append(key)
        else: #choose from inactives
            for key in current_sprites[entity_id].inactive_dependants.keys():
                candidate_dependant_entities.append(key)
        #choose a random dependant from the master entity
        dependant_index = random.randint(0, len(candidate_dependant_entities)-1)
        dependant_entity_id = candidate_dependant_entities[dependant_index]
    #passed in a value to use for the main entity, find the dependant
    elif dependant_entity_id is None:
        try:
            if len(current_sprites[entity_id].dependant_sprite_nodes) < 1  and \
                    len(current_sprites[entity_id].inactive_dependants) < 1:
                return [0,0]
            candidate_dependant_entities = list()
            # the key is the dependant_entity_id
            if len(current_sprites[entity_id].dependant_sprite_nodes) > 0:
                for key in current_sprites[entity_id].dependant_sprite_nodes.keys():
                    candidate_dependant_entities.append(key)
            else:  # choose from inactives
                for key in current_sprites[entity_id].inactive_dependants.keys():
                    candidate_dependant_entities.append(key)
            # choose a random dependant from the master entity
            dependant_index = random.randint(0, len(candidate_dependant_entities) - 1)
            dependant_entity_id = candidate_dependant_entities[dependant_index]
        except Exception as e:
            if GRID_DEBUG_PRINT_FUNCTIONS:
                print("Exception caught removing entity dependancy")
                print(e)
            return [0,0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('remove from entity: ' + str(entity_id) + ", dependant: " + str(dependant_entity_id))
    game_engine_mock.removeEntityDependancy(entity_id, dependant_entity_id)
    return [entity_id, dependant_entity_id]

'''
Scroll the particle associated with a sprite the amount passed in
'''
def panSprite(game_engine_mock, entity_id = None, pan = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
        pan = input("pan: <#,#,#>\n>>>")
        pan = pan.split(',')
        pan = stringListToIntList(pan)
    elif entity_id == 0: #NOP
        return [0,0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Entity id: "+str(entity_id)+' Pan: ' + str(pan))
    game_engine_mock.panSprite(entity_id, pan) #scripted
    return [entity_id, pan]

def panSpriteRandom(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0, 0]
    direction = randomDirection()
    pan_x = 0
    pan_y = 0
    pan_z = 0
    if direction == "horizontal":
        pan_x = random.randint(-GRID_PAN_SPRITE_AMT, GRID_PAN_SPRITE_AMT)
    elif direction == "vertical":
        pan_y = random.randint(-GRID_PAN_SPRITE_AMT, GRID_PAN_SPRITE_AMT)
    elif direction == "zshift":
        pan_z = random.randint(-2, 2)
    else:
        pan_x = random.randint(-GRID_PAN_SPRITE_AMT, GRID_PAN_SPRITE_AMT)
        pan_y = random.randint(-GRID_PAN_SPRITE_AMT, GRID_PAN_SPRITE_AMT)
        pan_z = random.randint(-2, 2)
    pan = [pan_x, pan_y, pan_z]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Entity id: "+str(entity_id)+' Pan: ' + str(pan))
    game_engine_mock.panSprite(entity_id, pan) #scripted
    return [entity_id, pan]
'''
Move the particle associated with a sprite to coordinates passed in
'''
def moveSprite(game_engine_mock, entity_id = None, move = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
        move = input("move: <#,#,#>\n>>>")
        move = move.split(',')
        move = stringListToIntList(move)
    elif entity_id == 0: #NOP
        return [0,0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Entity id: "+str(entity_id)+' Move: ' + str(move))
    game_engine_mock.moveSprite(entity_id, move) #scripted
    return [entity_id, move]

def moveSpriteRandom(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0, 0]
    scene_id = game_engine_mock.getEntitySceneId(entity_id)
    if scene_id == 0:
        print("getEntitySceneId failed to find, ",entity_id)
        assert False #Why didn't we find this entity?
    world_size = game_engine_mock.getSceneWorldSize(scene_id)
    move = [random.randint(0, world_size[0] - 1),
            random.randint(0, world_size[1] - 1),
            random.randint(-100, 100)]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Entity id: "+str(entity_id)+' Move: ' + str(move))
    game_engine_mock.moveSprite(entity_id, move) #scripted
    return [entity_id, move]

'''
behaviorFSM updated the animation
'''
def flipAnimation(game_engine_mock, entity_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0]
    game_engine_mock.flipAnimation(entity_id)
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Entity id: "+str(entity_id)+" flip animation")
    return [entity_id]

def setBehaviorState(game_engine_mock, entity_id = None, behavior_state_id = None):
    if entity_id is None: #manual call
        entity_id = [0]
        while not isValidChoice('int_1+', entity_id):
            entity_id = int(input("entity_id: <#>\n>>>"))
        behavior_state_id = [0]
        while not isValidChoice('int_any', behavior_state_id):
            behavior_state_id = int(input("behavior_state_id: <#> (-1 for a random value)\n>>>"))
    elif entity_id == -1:
        entity_id = chooseRandomEntityId(game_engine_mock)
    if entity_id == 0:  # NOP
        return [0, 0]
    if behavior_state_id == -1: #Note, None is not a valid scripted value, only passed in for a manual call
        behavior_state_id = random.randint(GRID_BEHAVIOR_ID_MIN, GRID_BEHAVIOR_ID_MAX)
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print("Entity id: "+str(entity_id)+" Behavior state: " + str(behavior_state_id))
    game_engine_mock.setBehaviorState(entity_id, behavior_state_id)
    return [entity_id, behavior_state_id]

'''
Adjust the camera position from it's current location
'''
def panCamera(game_engine_mock, camera_id = None, pan = None):
    if pan is None: #manual call
        pan = input("pan: <#,#>\n>>>")
        pan = pan.split(',')
        pan = stringListToIntList(pan)
        game_engine_mock.panCamera(pan)
    if camera_id is None: #manual call
        while not isValidChoice('int_1+', camera_id):
            camera_id = int(input("camera_id: <#>\n>>>"))
    if camera_id == 0: #treat as NOP
        return [0,0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Pan camera: ',str(camera_id)," ",str(pan))
    game_engine_mock.panCamera(camera_id, pan)
    return [camera_id, pan]

def panCameraRandom(game_engine_mock):
    direction = randomDirection()
    if direction == "horizontal":
        pan_x = random.randint(-GRID_PAN_CAMERA_AMT, GRID_PAN_CAMERA_AMT)
        pan_y = 0
    elif direction == "vertical":
        pan_x = 0
        pan_y = random.randint(-GRID_PAN_CAMERA_AMT, GRID_PAN_CAMERA_AMT)
    else:
        pan_x = random.randint(-GRID_PAN_CAMERA_AMT, GRID_PAN_CAMERA_AMT)
        pan_y = random.randint(-GRID_PAN_CAMERA_AMT, GRID_PAN_CAMERA_AMT)
    pan = [pan_x, pan_y]
    candidate_camera_ids = list()
    for camera_id_key, camera in game_engine_mock._camera_manager._cameras.items():
        if camera.scene is not None:
            candidate_camera_ids.append(camera_id_key)
    if len(candidate_camera_ids) == 0:
        return [0,0] #treat as nop
    camera_id_index = random.randint(0, len(candidate_camera_ids) - 1)
    camera_id = candidate_camera_ids[camera_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Pan camera: ',camera_id," ",str(pan))
    game_engine_mock.panCamera(camera_id, pan) #scripted
    return [camera_id, pan]

'''
Place the camera in a completely different spot based on new coordinates
'''
def moveCamera(game_engine_mock, camera_id = None, move = None):
    if move is None: #manual call
        move = input("move: <#,#>\n>>>")
        move = move.split(',')
        move = stringListToIntList(move)
    if camera_id is None: #manual call
        while not isValidChoice('int_1+', camera_id):
            camera_id = int(input("camera_id: <#>\n>>>"))
    if camera_id == 0: #treat as NOP
        return [0,0]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Move camera: ',str(camera_id)," ",str(move))
    game_engine_mock.moveCamera(camera_id, move) #scripted
    return [camera_id, move]

def moveCameraRandom(game_engine_mock):
    candidate_camera_ids = list()
    for camera_id_key, camera in game_engine_mock._camera_manager._cameras.items():
        if camera.scene is not None:
            candidate_camera_ids.append(camera_id_key)
    if len(candidate_camera_ids) == 0:
        return [0,0] #treat as nop
    camera_id_index = random.randint(0, len(candidate_camera_ids) - 1)
    camera_id = candidate_camera_ids[camera_id_index]
    camera = game_engine_mock._camera_manager._cameras[camera_id]
    camera_position = camera.getPosition()
    # camera will correct for moving outside of viewing boundary
    direction = randomDirection()
    scene_id = camera.scene.scene_id
    world_size = game_engine_mock.getSceneWorldSize(scene_id)
    if direction == "horizontal":
        move_x = random.randint(0, world_size[0])
        move_y = camera_position[1]
    elif direction == "vertical":
        move_x = camera_position[0]
        move_y = random.randint(0, world_size[1])
    else:
        move_x = random.randint(0, world_size[0])
        move_y = random.randint(0, world_size[1])
    move = [move_x, move_y]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Move camera: ',str(camera_id)," ",str(move))
    game_engine_mock.moveCamera(camera_id, move) #scripted
    return [camera_id, move]

#only allows you to toggle tests on off - could update to have more fine grained control in the future if needed
def configureTests(test_config = None):
    if test_config is None: #manual call
        test_config = -1
        while test_config not in [0,1]:
            try:
                test_config = int(input(GRID_CONFIGURE_TEST_MENU))
            except:
                test_config = -1
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Configure Tests: ' + str(test_config))
    return [test_config]

#The key in recreating scripts is that as scene_ids are always incremented when creating a scne
#So since we always create the same number of scenes in the same points in a script, the scene_ids are constant
def createScene(game_engine_mock, world_size = -1, cell_size = -1, tile_size = -1):
    if len(game_engine_mock.getSceneIds()) > GRID_MAX_SCENES:
        return -1 #This will prevent more scenes being made, or layers/cameras being added to current
    #random vals
    if world_size == -1 or world_size is None: #no manual setting option for now
        #SET WORLD SIZE
        width_px = int(random.randint(GRID_WORLD_SIZE_MIN, GRID_WORLD_SIZE_MAX))
        height_px = int(random.randint(GRID_WORLD_SIZE_MIN, GRID_WORLD_SIZE_MAX))
        world_size = [width_px, height_px]
        #SET CELL SIZE
        width_px = int(random.randint(GRID_CELL_SIZE_MIN, GRID_CELL_SIZE_MAX))
        height_px = int(random.randint(GRID_CELL_SIZE_MIN, GRID_CELL_SIZE_MAX))
        #Cell not allowed to be larger than world
        if width_px > world_size[0]:
            width_px = world_size[0]
        if height_px > world_size[1]:
            height_px = world_size[1]
        cell_size = [width_px, height_px]
        # SET TILE SIZE
        width_px = int(random.randint(GRID_TILE_SIZE_MIN, GRID_TILE_SIZE_MAX))
        height_px = int(random.randint(GRID_TILE_SIZE_MIN, GRID_TILE_SIZE_MAX))
        #Tile must be slammer than cell
        if width_px > cell_size[0]:
            width_px = cell_size[0]
        if height_px > cell_size[1]:
            height_px = cell_size[1]
        #keeps trying to find a tile size that evenely divides the cell size by walking down by 1 at a time
        while cell_size[0] % width_px !=0:
            width_px -=1
        while cell_size[1] % height_px !=0:
            height_px -=1
        tile_size = [width_px, height_px]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Create scene: ', world_size, cell_size, tile_size)
    scene_id = game_engine_mock.createScene(world_size, cell_size, tile_size)
    return scene_id, [world_size, cell_size, tile_size]

def removeScene(game_engine_mock, scene_id = -1):
    if scene_id == 0: #Treat as a NOP
        return [0]
    scenes = game_engine_mock._scene_manager._scenes
    if scene_id is None: #manual call
        scene_id = [0]
        while not isValidChoice('int_1+', scene_id):
            scene_id = int(input("camera_id: <#>\n>>>"))
        if scenes.get(scene_id) is None:
            print("scene_id does not exist: ",scene_id)
            return [0]
        if scenes.get(scene_id).is_active:
            print("Scene is active and cannot be removed: ", scene_id)
            return [0]
    # can only remove a scene that is not active
    candidate_scene_ids = list()
    for scene_id_key, scene in scenes.items():
        if not scene.is_active:
            candidate_scene_ids.append(scene_id_key)
    if len(candidate_scene_ids) == 0:
        return [0]
    if scene_id == -1: #random:
        scene_id_index = random.randint(0, len(candidate_scene_ids)-1)
        scene_id = candidate_scene_ids[scene_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Remove scene: ', scene_id)
    game_engine_mock.removeScene(scene_id)
    return [scene_id]

def createSceneLayer(game_engine_mock, scene_id = -1, layer_id = -1, layer_type = -1):
    #treat 0 as a NOP
    if scene_id == 0:
        return [0,0,0]
    if scene_id is None:  # manual call
        scene_id = [0]
        while not isValidChoice('int_1+', scene_id):
            scene_id = int(input("scene_id: <#>\n>>>"))
        layer_id = [0]
        while not isValidChoice('int_1+', layer_id):
            scene_id = int(input("layer_id: <#>\n>>>"))
        layer_type = [0]
        while not isValidChoice('int_1+', scene_id):
            layer_type = int(input("layer_type: <#>\n>>>"))
    #random choice
    if scene_id == -1:
        current_scenes = game_engine_mock.getSceneIds()
        if len(current_scenes) < 1:
            return [0,0,0]
        scene_id_index = random.randint(0, len(current_scenes)-1)
        scene_id = current_scenes[scene_id_index]
    current_layer_ids = game_engine_mock.getLayerIds(scene_id)
    if len(current_layer_ids) > GRID_MAX_TEST_LAYERS: #arbitrarily have set max number of layers
        return [0,0,0] #this scene is full of layers, return a NOP
    if layer_id == -1:
        #randomly choose a unique layer id for this scene
        while layer_id  == -1 or layer_id in current_layer_ids:
            layer_id = random.randint(0, GRID_MAX_TEST_LAYERS)
    if layer_type == -1:
        layer_type = random.randint(GRID_LAYERTYPE_MIN, GRID_LAYERTYPE_MAX)
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Add Scene Layer: ',scene_id,layer_id,layer_type)
    game_engine_mock.createSceneLayer(scene_id,layer_id,layer_type)
    return [scene_id,layer_id,layer_type]

def removeSceneLayer(game_engine_mock, scene_id = -1, layer_id = -1):
    #treat 0 as a NOP
    if scene_id == 0:
        return [0,0]
    current_scenes = game_engine_mock.getSceneIds()
    if len(current_scenes) < 1:
        return [0,0]
    if scene_id is None:  # manual call
        scene_id = [0]
        while not isValidChoice('int_1+', scene_id):
            scene_id = int(input("scene_id: <#>\n>>>"))
        layer_id = [0]
        while not isValidChoice('int_1+', layer_id):
            scene_id = int(input("layer_id: <#>\n>>>"))
    #random choice
    if scene_id == -1:
        scene_id_index = random.randint(0, len(current_scenes)-1)
        scene_id = current_scenes[scene_id_index]
    current_layer_ids = game_engine_mock.getLayerIds(scene_id)
    if len(current_layer_ids) < 1:
        return [0,0]
    if layer_id == -1:
        layer_id_index = random.randint(0, len(current_layer_ids)-1)
        layer_id = current_layer_ids[layer_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Remove Scene Layer: ',scene_id,layer_id)
    game_engine_mock.removeSceneLayer(scene_id,layer_id)
    return [scene_id,layer_id]

def activateScene(game_engine_mock, scene_id = -1):
    # treat 0 as a NOP
    if scene_id == 0:
        return [0]
    if scene_id is None:  # manual call
        scene_id = [0]
        while not isValidChoice('int_1+', scene_id):
            scene_id = int(input("scene_id: <#>\n>>>"))
    #random choice
    if scene_id == -1:
        inactive_scene_ids = game_engine_mock.getInactiveSceneIds()
        if len(inactive_scene_ids) == 0 :
            return [0]
        scene_id_index = random.randint(0, len(inactive_scene_ids)-1)
        scene_id = inactive_scene_ids[scene_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('activate scene: ',scene_id)
    game_engine_mock.activateScene(scene_id)
    return [scene_id]

def deactivateScene(game_engine_mock, scene_id = -1):
    # treat 0 as a NOP
    if scene_id == 0:
        return [0]
    if scene_id is None:  # manual call
        scene_id = [0]
        while not isValidChoice('int_1+', scene_id):
            scene_id = int(input("scene_id: <#>\n>>>"))
    # random choice
    if scene_id == -1:
        active_scene_ids = game_engine_mock.getActiveSceneIds()
        if len(active_scene_ids) == 0:
            return [0]
        scene_id_index = random.randint(0, len(active_scene_ids) - 1)
        scene_id = active_scene_ids[scene_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('deactivate scene: ', scene_id)
    game_engine_mock.deactivateScene(scene_id)
    return [scene_id]

def createCamera(game_engine_mock, window_size = -1, activate_range = -1, deactivate_range = -1):
    if window_size == -1: #random_choice
        width_px = int(random.randint(GRID_SCREEN_SIZE_MIN, GRID_SCREEN_SIZE_MAX))
        height_px = int(random.randint(GRID_SCREEN_SIZE_MIN, GRID_SCREEN_SIZE_MAX))
        window_size = [width_px, height_px]
        #Set Hysteresis
        activate_x = int(random.randint(GRID_HYSTERESIS_MIN, GRID_HYSTERESIS_MAX))
        activate_y = int(random.randint(GRID_HYSTERESIS_MIN, GRID_HYSTERESIS_MAX))
        activate_range = [activate_x, activate_y]
        deactivate_x = int(random.randint(GRID_HYSTERESIS_MIN, GRID_HYSTERESIS_MAX))
        deactivate_y = int(random.randint(GRID_HYSTERESIS_MIN, GRID_HYSTERESIS_MAX))  # triangular biasis towards midpoint
        deactivate_range = [deactivate_x, deactivate_y]
        #activate must be less than deactivate in both x and y axis
        if activate_range[0] >= deactivate_range[0]:
            activate_range[0] = deactivate_range[0] - 1
        if activate_range[1] >= deactivate_range[1]:
            activate_range[1] = deactivate_range[1] - 1

    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Create camera: ', window_size, activate_range, deactivate_range)
    camera_id = game_engine_mock.createCamera(window_size, activate_range, deactivate_range)
    return camera_id, [window_size, activate_range, deactivate_range]

def removeCamera(game_engine_mock, camera_id = -1):
    if camera_id == 0: #Treat as a NOP
        return [0]
    cameras = game_engine_mock._camera_manager._cameras
    if camera_id is None: #manual call
        camera_id = [0]
        while not isValidChoice('int_1+', camera_id):
            camera_id = int(input("camera_id: <#>\n>>>"))
        if cameras.get(camera_id) is None:
            print("Camera_ID does not exist: ",camera_id)
            return [0]
        if cameras.get(camera_id).scene is not None:
            print("Camera is attached and cannot be removed: ",camera_id)
            return [0]
    # can only remove a camera that is not attached
    candidate_camera_ids = list()
    for camera_id_key, camera in cameras.items():
        if camera.scene is None:
            candidate_camera_ids.append(camera_id_key)
    if len(candidate_camera_ids) == 0:
        return [0]
    if camera_id == -1: #random:
        camera_id_index = random.randint(0, len(candidate_camera_ids)-1)
        camera_id = candidate_camera_ids[camera_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Remove Camera: ', camera_id)
    game_engine_mock.removeCamera(camera_id)
    return [camera_id]

def attachCamera(game_engine_mock, scene_id = -1, camera_id = -1, position = -1):
    if camera_id == 0:
        return [0,0] #treat as NOP
    scene_ids = game_engine_mock.getSceneIds()
    if len(scene_ids) == 0:
        return [0,0]
    # can only attach a camera that is not attached
    candidate_camera_ids = list()
    for camera_id_key, camera in game_engine_mock._camera_manager._cameras.items():
        if camera.scene is None:
            candidate_camera_ids.append(camera_id_key)
    if len(candidate_camera_ids) == 0:
        return [0,0]
    if camera_id is None: #manual call
        camera_id = [0]
        while not isValidChoice('int_1+', camera_id) or not camera_id in candidate_camera_ids:
            camera_id = int(input("camera_id: <#>\n>>>"))
    if camera_id == -1: #random choice
        camera_id_index = random.randint(0, len(candidate_camera_ids)-1)
        camera_id = candidate_camera_ids[camera_id_index]
    if scene_id is None: #manual call
        scene_id = [0]
        while not isValidChoice('int_1+', scene_id):
            scene_id = int(input("scene_id: <#>\n>>>"))
    if scene_id == -1:
        scene_id_index = random.randint(0, len(scene_ids)-1)
        scene_id = scene_ids[scene_id_index]
    #random position
    if position == -1 or position is None:
        world_size = game_engine_mock.getSceneWorldSize(scene_id)
        start_x = random.randint(0, world_size[0] -1)
        start_y = random.randint(0, world_size[1] -1)
        position = [start_x, start_y]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Attach camera: ', scene_id, camera_id, position)
    game_engine_mock.attachCamera(scene_id, camera_id, position)
    return [scene_id, camera_id, position]

def detachCamera(game_engine_mock, camera_id = -1):
    if camera_id == 0:
        return [0] #treat as a NOP
    #can only detach a camera that is attached
    candidate_camera_ids = list()
    for camera_id_key, camera in game_engine_mock._camera_manager._cameras.items():
        if camera.scene is not None:
            candidate_camera_ids.append(camera_id_key)
    if len(candidate_camera_ids) == 0:
        return [0]
    if camera_id is None: #Manual call
        camera_id = [0]
        while not isValidChoice('int_1+', camera_id) or not camera_id in candidate_camera_ids:
            camera_id = int(input("camera_id: <#>\n>>>"))
    if camera_id == -1: #random choice
        camera_id_index = random.randint(0, len(candidate_camera_ids)-1)
        camera_id = candidate_camera_ids[camera_id_index]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Detach Camera: ', camera_id)
    game_engine_mock.detachCamera(camera_id)
    return [camera_id]

def setCameraWindowSize(game_engine_mock, camera_id = -1, window_size = -1):
    if camera_id == 0:
        return [0]  # treat as a NOP
    candidate_camera_ids = list()
    for camera_id_key, camera in game_engine_mock._camera_manager._cameras.items():
        candidate_camera_ids.append(camera_id_key)
    if len(candidate_camera_ids) == 0:
        return [0] # treat as a NOP
    if camera_id == -1:  # random choice
        camera_id_index = random.randint(0, len(candidate_camera_ids) - 1)
        camera_id = candidate_camera_ids[camera_id_index]
        #we will do a small tweak to the size 75% of the time, and a completely new size 25%
        if random.randint(1,4) == 1:
            width_px = int(random.randint(GRID_SCREEN_SIZE_MIN, GRID_SCREEN_SIZE_MAX))
            height_px = int(random.randint(GRID_SCREEN_SIZE_MIN, GRID_SCREEN_SIZE_MAX))
            window_size = [width_px, height_px]
        else:
            current_size = game_engine_mock.getCameraWindowSize(camera_id)
            #change just x, just y, or both
            change_type = random.randint(1, 3)
            if change_type == 1:
                #just change x
                x_change = random.randint(-15,15) #-15% to 15% change
                x_width = int(current_size[0] + (x_change*.01)*current_size[0])
                if x_width <GRID_SCREEN_SIZE_MIN:
                    x_width = GRID_SCREEN_SIZE_MIN
                if x_width > GRID_SCREEN_SIZE_MAX:
                    x_width = GRID_SCREEN_SIZE_MAX
                window_size = [x_width, current_size[1]]
            elif change_type == 2:
                # just change y
                y_change = random.randint(-15, 15)  # -15% to 15% change
                y_height = int(current_size[1] + (y_change * .01) * current_size[1])
                if y_height < GRID_SCREEN_SIZE_MIN:
                    y_height = GRID_SCREEN_SIZE_MIN
                if y_height > GRID_SCREEN_SIZE_MAX:
                    y_height = GRID_SCREEN_SIZE_MAX
                window_size = [current_size[0], y_height]
            else:
                #change x and y
                x_change = random.randint(-15, 15)  # -%15 to15% change
                x_width = int(current_size[0] + (x_change * .01) * current_size[0])
                if x_width < GRID_SCREEN_SIZE_MIN:
                    x_width = GRID_SCREEN_SIZE_MIN
                if x_width > GRID_SCREEN_SIZE_MAX:
                    x_width = GRID_SCREEN_SIZE_MAX
                y_change = random.randint(-15, 15)  # -%15 to15% change
                y_height = int(current_size[1] + (y_change * .01) * current_size[1])
                if y_height < GRID_SCREEN_SIZE_MIN:
                    y_height = GRID_SCREEN_SIZE_MIN
                if y_height > GRID_SCREEN_SIZE_MAX:
                    y_height = GRID_SCREEN_SIZE_MAX
                window_size = [x_width, y_height]
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('Set camera window size: ',camera_id, window_size)
    game_engine_mock.setCameraWindowSize(camera_id, window_size)
    return [camera_id, window_size]

def setSubscriptRunthroughs(subscript_runthroughs = None):
    if subscript_runthroughs is None: #manual call
        subscript_runthroughs = [0]
        while not isValidChoice('int_1+', subscript_runthroughs):
            subscript_runthroughs = input("subscript_runthroughs: <#>\n>>>")
    else: #unlikely to get here as we don't need to call this method on an automated call
        if GRID_DEBUG_PRINT_FUNCTIONS:
            print('subscript_runthroughs: ' + str(subscript_runthroughs))
    return [subscript_runthroughs]

def randomAction():
    val = random.randint(1, 407)

    if 1 <= val <= 400:
        return GRID_CHOICE_RANDOM_SPRITE_ACTION, [None]
    elif 401 <= val <= 403:
        return GRID_CHOICE_RANDOM_CAMERA_ACTION, [None]
    elif 404 <= val <= 406:
        return GRID_CHOICE_RANDOM_SCENE_ACTION, [None]
    elif 407 <= val <= 407:
        return GRID_CHOICE_UPDATE, [None]

    print("You should not get here in randomAction")
    assert False

def randomCameraAction():
    val = random.randint(1,6)

    if 1 <= val <= 2:
        return GRID_CHOICE_MOVE_CAMERA_RANDOM, [None]
    elif 3 <= val <= 5:
        return GRID_CHOICE_PAN_CAMERA_RANDOM, [-1]
    elif 6 <= val <= 6:
        return GRID_CHOICE_SET_CAMERA_SIZE, [-1, -1]

    print("You should not get here in randomCameraAction")
    assert False

#Returns a random choice and appropriate args
def randomSceneAction():
    val = random.randint(1,124)

    if 1 <= val <= 15:
        return GRID_CHOICE_ADD_SCENE, [-1,-1,-1]
    elif 16 <= val <= 20:
        return GRID_CHOICE_REMOVE_SCENE, [-1]
    elif 21 <= val <= 39:
        return GRID_CHOICE_ACTIVATE_SCENE, [-1]
    elif 40 <= val <= 48:
        return GRID_CHOICE_DEACTIVATE_SCENE, [-1]
    elif 49 <= val <= 63:
        return GRID_CHOICE_CREATE_CAMERA, [-1,-1,-1]
    elif 64 <= val <= 72:
        return GRID_CHOICE_REMOVE_CAMERA, [-1]
    elif 73 <= val <= 90:
        return GRID_CHOICE_ATTACH_CAMERA, [-1,-1]
    elif 91 <= val <= 100:
        return GRID_CHOICE_DETACH_CAMERA, [-1]
    elif 101 <= val <= 115:
        return GRID_CHOICE_ADD_LAYER, [-1]
    elif 116 <= val <= 124:
        return GRID_CHOICE_REMOVE_LAYER, [-1]

    print("You should not get here in randomSceneAction")
    assert False

def randomSpriteAction():
    val = random.randint(1,595)

    if 1 <= val <= 120:
        return GRID_CHOICE_PAN_SPRITE_RANDOM, [-1]
    elif 121 <= val <= 180:
        return GRID_CHOICE_MOVE_SPRITE_RANDOM, [-1]

    elif 181 <= val <= 275:
        return GRID_CHOICE_FLIP_ANIMATION, [-1]
    elif 276 <= val <= 300:
        return GRID_CHOICE_SET_BEHAVIOR_STATE, [-1,-1]

    elif 301 <= val <= 355:
        return GRID_CHOICE_ADD_ENTITY_DEPENDANT, [-1, -1]
    elif 356 <= val <= 373:
        return GRID_CHOICE_REMOVE_ENTITY_DEPENDANT, [-1, -1]

    elif 374 <= val <= 376:
        return GRID_CHOICE_ACTIVATE_ENTITY, [-1]
    elif 377 <= val <= 378:
        return GRID_CHOICE_DEACTIVATE_ENTITY, [-1]

    elif 379 <= val <= 380:
        return GRID_CHOICE_SET_ENTITY_ALWAYS_ACTIVE, [-1]
    elif 381 <= val <= 382:
        return GRID_CHOICE_REMOVE_ENTITY_ALWAYS_ACTIVE, [-1]

    elif 383 <= val <= 384:
        return GRID_CHOICE_SET_SPRITE_VISIBLE, [-1]
    elif 385 <= val <= 386:
        return GRID_CHOICE_SET_SPRITE_INVISIBLE, [-1]

    elif 387 <= val <= 388:
        return GRID_CHOICE_SET_SPRITE_ETHEREAL, [-1]
    elif 389 <= val <= 390:
        return GRID_CHOICE_SET_SPRITE_TANGIBLE, [-1]

    elif 391 <= val <= 392:
        return GRID_CHOICE_ACTIVATE_ENTITY_PHYSICS, [-1]
    elif 393 <= val <= 394:
        return GRID_CHOICE_DEACTIVATE_ENTITY_PHYSICS, [-1]

    elif 395 <= val <= 396:
        return GRID_CHOICE_ACTIVATE_ENTITY_BEHAVIOR, [-1]
    elif 397 <= val <= 398:
        return GRID_CHOICE_DEACTIVATE_ENTITY_BEHAVIOR, [-1]

    elif 399 <= val <= 400:
        return GRID_CHOICE_ACTIVATE_ENTITY_AI, [-1]
    elif 401 <= val <= 402:
        return GRID_CHOICE_DEACTIVATE_ENTITY_AI, [-1]

    elif 403 <= val <= 560:
        return GRID_CHOICE_INSERT_SPRITE, [-1]
    elif 561 <= val <= 595:
        return GRID_CHOICE_REMOVE_SPRITE, [-1]

    print("You should not get here in randomSpriteAction")
    assert False

#Return a random existing entity ID, or 0 if there are no IDs
def chooseRandomEntityId(game_engine_mock):
    all_entity_ids = game_engine_mock.getAllTestingEntityIds()
    if len(all_entity_ids) > 0:
        entity_id_index = random.randint(0, len(all_entity_ids) - 1)
        current_entity_id = all_entity_ids[entity_id_index]
        if GRID_DEBUG_PRINT_FUNCTIONS:
            print('Set current entity id: ' + str(current_entity_id))
        return current_entity_id
    else:
        return 0

def resetGameEngine(game_engine_mock):
    if GRID_DEBUG_PRINT_FUNCTIONS:
        print('RESET ENGINE')
    game_engine_mock.resetEngine()

def execCommand(command = None):
    if command is None:
        command = str(input("enter command"))
    exec(command)
    return [command]

def printSpriteStates(game_engine_mock, entity_ids):
    if GRID_DEBUG_PRINT_FUNCTIONS:
        try:
            sprites = game_engine_mock.getAllSprites()
            for entity_id in entity_ids:
                if sprites.get(entity_id) is not None:
                    sprite_state = sprites[entity_id].current_sprite_state
                    state_string = str(sprite_state).replace("<Rendering.Scene_sprite_states.", "")
                    state_string = state_string.replace(" object at ", "")
                    state_strings = state_string.split("0x")
                    state_string = state_strings[0]
                    print("SPRITESTATE " + str(entity_id)+": " + str(state_string))
        except Exception as e:
            print("Exception caught in printSpriteStates")
            print(e)


#test collection is a list of test suites
    #each entry is a tuple with index 0 true if test suite should run, and the test suite as index 1
#a test suite is a list of test functions
    #each entry is a tuple with index 0 true if test should run, and the test function is index 1
#run the test by passing the game_engine_mock, test returns true/false
def runSceneTests(game_engine_mock, test_collection):
    try:
        for test_suite in test_collection:
            if test_suite[0]:
                for test in test_suite[1]:
                    if test[0]:
                        if GRID_DEBUG_PRINT_FUNCTIONS:
                            print("Running test: "+ str(test[1].__name__))
                        if not test[1](game_engine_mock):
                            print("Test has failed")
                            assert(1==2)
    except Exception as e:
        print(e)
        assert False