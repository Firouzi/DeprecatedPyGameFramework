"""
For testing scene_layer_grid.  Allows manually adding and manipulating entites, or running scripts.

Scripts can be loaded from JSON, or each action can be commanded manually.
Whether from script, or manual, all actions are saved to an ouput script to allow re-running the same scenario.
Any random numbered actions will be saved to the script so that the scenario always runs the same way.

kasidie
Afon001
Bear1475
TestMark
hrfirouzi@gmail.com
HRFMa-9725
fb
ashley.christensen1475@yahoo.com ~ Kilo1475!
gm
ashley.firouzi1475@gmail.vom ! Polars2017!
ashley.fondren1475@gmail.vom ~ 96bLLNXGJucrn6C2)
linkedIN
ashley.firouzi1475@gmail.vom ~ Bear1475
GoodReads
ashley.firouzi1475@gmail.com ~ Bear1475

"""

from time import sleep

from Game_Scene.Test.Test_System.Game_enging_testing_functions import *
from Game_Scene.Test.Mock_Classes.Game_engine_mock import GameEngineMock
from Game_Scene.Test.Test_System.Testing_script_io import ScriptSaver, ScriptLoader
from Game_Scene.Test.Test_Script.Test_Conditions.Test_condition_builder import buildTestConditionManager
from Game_Scene.Test.Agent_Chaos.Agent_chaos import AgentChaos
### Possible Features
#Add choice for save/load state (when supported)

from Game_Scene.Test.Test_Suites import test_Scene_layer, test_Scene_grid, test_Scene_cell, test_Scene_node
from Game_Scene.Test.Test_Suites import test_Entity_manager, test_Scene_manager, test_Scene_camera

#Set a True/False to run the test
SCENE_LAYER_TEST_SUITE = (
    [True, test_Scene_layer._testEntityReferences_], #Very slow
    [True, test_Scene_layer._testVerifyActiveEntities_],
    [True, test_Scene_layer._testSceneLayerReferences_],
    [True, test_Scene_layer._testEntityByLayerId_],
    [True, test_Scene_layer._testCurrentLayerIds_],
)

SCENE_GRID_TEST_SUITE = (
    [True, test_Scene_grid._testOffScreenActives_],
    [True, test_Scene_grid._testEntityInGridInDict_],
    [True, test_Scene_grid._testCloneParentRelationship_],
    [True, test_Scene_grid._testMasterCellsActiveState_],
    [True, test_Scene_grid._testCellBordersSizes_],
    [True, test_Scene_grid._testAllEntitiesInGridUnique_],
    [True, test_Scene_grid._testCellMetaDataMatchesMaster_],
    [True, test_Scene_grid._testMasterCellsInactiveState_],
)

SCENE_CELL_TEST_SUITE = (
    [True, test_Scene_cell._testCellsAreSorted_],
    [True, test_Scene_cell._testLinkedListsAreConsistent_],
    [True, test_Scene_cell._testSpritesStayInBorders_],
    [True, test_Scene_cell._testInvisibleSpritesLists_],
    [True, test_Scene_cell._testSceneCellReferences_],
)

SCENE_NODE_TEST_SUITE =(
    [False, test_Scene_node._testSpriteComponentReferences_],
    [False, test_Scene_node._testNodeGridRefMatchesSceneRef_],
    [True, test_Scene_node._testSpriteRenderCoordinates_],
    [False, test_Scene_node._testSpriteBehaviorState_],
    [False, test_Scene_node._testOffscreenActiveNetwork_],
    [True, test_Scene_node._testSpritesCreateNeededClones_],
    [False, test_Scene_node._testParentCloneRefConsistent_],
    [True, test_Scene_node._testWorldPositionGroundPosition_],
    [False, test_Scene_node._testDependantsInSameLayer_],
    [False, test_Scene_node._testCloneParentVisibilityMatches_],
)

#_testActiveInactiveAcrossComponents_
#These tests are loop heavy (slow!)
ENTITY_MANAGER_TEST_SUITE = (
    [True, test_Entity_manager._testActiveInactiveAcrossComponents_],
    [True, test_Entity_manager._testEntityStatusIdenticalAcrossDependants_],
    [True, test_Entity_manager._testEntityDependancyConsistent_],
    [True, test_Entity_manager._testSpriteStateEntityStatusMatch_],
    [True, test_Entity_manager._testEntityStatusSpriteDependantEqual_],
    [True, test_Entity_manager._testEntityManagerCorrectScene_],
    [True, test_Entity_manager._testOnscreenEntityIds_],
)

SCENE_MANAGER_TEST_SUITE =(
    [True, test_Scene_manager._testSceneReferencesMatch_],
    [True, test_Scene_manager._testEntityInCorrectSceneManagers_],
    [True, test_Scene_manager._testEntitySceneMap_],
    [True, test_Scene_manager._testSceneSizeParameters_],
)

SCENE_CAMERA_TEST_SUITE =(
    [True, test_Scene_camera._testCameraWithinWorldBoundary_],
)

SCENE_TEST_COLLECTION = (
    [False, SCENE_LAYER_TEST_SUITE ],
    [False, SCENE_GRID_TEST_SUITE ],
    [False, SCENE_CELL_TEST_SUITE ],
    [True, SCENE_NODE_TEST_SUITE ],
    [False, ENTITY_MANAGER_TEST_SUITE ],
    [False, SCENE_MANAGER_TEST_SUITE ],
    [False, SCENE_CAMERA_TEST_SUITE ],
)

IS_RUN_TESTS = False
IS_CHECK_CONDITIONS = False
#Won't start running tests until the update count > TESTS_AFTER_UPDATE_CT
TESTS_AFTER_UPDATE_CT = 0

####### Set SCRIPT_LOAD_PATH, and SCRIPT as needed #######
    #Must define 1 and only 1 SCRIPT and SCRIPT_LOAD_PATH
#We can also point to a subfolder within the savedscripts directory
#these are auto saved anytime the test is running, whether commands are scripted or manual
#this allows replicating scenarios
#SCRIPT_LOAD_PATH = "12_10_2020__17_48_55_seq90"
IS_SAVED_RUN = False #this will get set to true in the try/except block below if needed
try:
    temp = SCRIPT
except: #So I don't have to keep commenting and uncommenting this line
    #This is setup as the default script to run, if we don't define SCRIPT_LOAD_PATH above
    SCRIPT = [[GRID_CHOICE_LOAD_SCRIPT, [9999]]]
try:#prevents havine to uncomment/comment SCRIPT_LOAD_PATH= None
    temp = SCRIPT_LOAD_PATH
    IS_SAVED_RUN = True
    # If we want to run from the auto saved path, start with script 0.  When auto saved they are daisy chained
    SCRIPT = [[GRID_CHOICE_LOAD_SCRIPT, [0]]]  # loading a generated script, start with script index 0
except:
    #If SCRIPT_LOAD_PATH is None, then we will use the main folder of scripts
    SCRIPT_LOAD_PATH = None
#Can setup a manual script, or start with an empty list for no scripted commands
#SCRIPT = [[GRID_CHOICE_SET_WORLD_SIZE,[1000,2000]]]
#SCRIPT = ['sprite_insert', 'sprite_insert', 'sprite_insert', 'sprite_insert', 'sprite_insert'] #using the shortcuts in the GRID_SCRIPT_MAP
#SCRIPT = list() # Start with no actions

#Can turn off step by step print statements, default is to use same status as func prints
    #but can set them independantly as needed
DEBUG_LOOP_PRINT = GRID_DEBUG_PRINT_FUNCTIONS
#for debug, before each update, print states of these entities
PRINT_SPRITE_STATES = list()
#PRINT_SPRITE_STATES = (193,584,405,337,171,578)
IS_SAVE_SCRIPT = True  #WARNING - If false, won't be able to re-run script of actions
REMOVE_PAST_SEQUENCE = True # If true, every time a new sequence is created, the previous sequence is archived and archived is deleted
MAX_LOOPS = 0 #25000000 #0 is infinite #5000000
MAX_UPDATES = 20000 #0 is infinite
MAX_EXCEPTIONS = 1 #quit if we have more, 0 is infinite
QUIT_IF_CONDITIONS_MET = False #if true, we exit test loop when all testing conditions have been met
PRINT_CONDITION_STATUS = 100 #print every numb updates (or 0 if not to print ever)
AGENT_CHAOS_RUN = 1 #Run agent chaos every this number of loops (0 for never)

LOOP_BREAK_POINTS = list() #Can make a list of loop #'s to set breakpoints on
LOOP_BREAK_POINTS.append(1000)

UPDATE_BREAK_POINTS = list() #like loop break points, but on the update #
UPDATE_BREAK_POINTS.append(25)


if __name__ == "__main__":
    print("scene_layer_grid test start")
    if not IS_SAVE_SCRIPT:
        print('***WARNING*** Script saving is turned OFF *****')
        sleep(0.5)
        print('***WARNING*** Script saving is turned OFF *****')
        sleep(0.5)
    is_all_tests = IS_RUN_TESTS
    for test_suite in SCENE_TEST_COLLECTION:
        if test_suite[0]:
            for test in test_suite[1]:
                if not test[0]:
                    is_all_tests = False
        else:
            is_all_tests = False
    if not is_all_tests:
        print('***WARNING*** Some tests are turned OFF *****')
        sleep(0.5)
        print('***WARNING*** Some tests are turned OFF *****')
        sleep(0.5)
    if TESTS_AFTER_UPDATE_CT > 0:
        print('***WARNING*** Tests OFF until update:', TESTS_AFTER_UPDATE_CT, ' *****')
        sleep(0.5)
        print('***WARNING*** Tests OFF until update:', TESTS_AFTER_UPDATE_CT, ' *****')
        sleep(0.5)

    game_engine_mock = GameEngineMock()
    test_condition_manager = buildTestConditionManager()
    agent_chaos = AgentChaos(is_save = not IS_SAVED_RUN, is_silent = not DEBUG_LOOP_PRINT)#GRID_DEBUG_PRINT_FUNCTIONS)
    exceptions_caught = 0
    update_count = 0
    #If script cleanup is true, any sanved script which is not tagged is deleted
    #Tag a script directory by starting the name of the directory with a letter
    script_loader = ScriptLoader(script_directory = SCRIPT_LOAD_PATH,
                                 script_cleanup = True)
    script_saver = ScriptSaver(GRID_SAVED_SCRIPTS_PATH,
                               is_save_script = IS_SAVE_SCRIPT & (not IS_SAVED_RUN))
    script_length = len(SCRIPT)
    #A main Script can load a sub_script.
    #sub_scripts can do everything a main script can do except load another sub script, or setup script repeats.
    subscript = list()
    #a main script can set the number of times a sub_script repeats
    subscript_runthroughs = 1 #number of times to run the current subscript
    subscript_numb_runs = 0 #number of times entire subscript has run (should run subscript_repeats times)
    numb_subscript = 0 #keep track sub_script index
    subscript_length = 0
    numb_script = 0 #mainscript index
    keep_going = True
    loops = 0
    current_scene_id = None #if we are doing scripted calls, there are times we may want to continue with current scene id
    current_camera_id = None #when doind scripted calls, can use this to attach last camera to a scene
    while keep_going:
        loops+=1
        choice = GRID_CHOICE_NOP #mainly to prevent a warning in the except branch below
        args = [None]  # if not a scripted call, this will be used
        try:
            if numb_subscript < subscript_length: #subscripts run to completion before returning to the main script
                if type(subscript[numb_subscript]) == list: #coded out each argument
                    choice = subscript[numb_subscript][0]
                    args = subscript[numb_subscript][1]
                    if DEBUG_LOOP_PRINT:
                        print(str(loops) +': ' + str(CHOICE_STRING_MAP[choice]))
                else: #using the script_map shortcut
                    key = subscript[numb_subscript]
                    if DEBUG_LOOP_PRINT:
                        print(str(loops) +': '+ str(key))
                    choice = GRID_SCRIPT_MAP[key][0]
                    args = GRID_SCRIPT_MAP[key][1]
                if choice == GRID_CHOICE_LOAD_SUBSCRIPT or choice == GRID_CHOICE_SET_SCRIPT_RUNTHROUGHS:
                    print("Subscripts cannot load subscripts or set repeat length")
                    choice = 9999
                    args = [None]
                numb_subscript +=1
                if numb_subscript == subscript_length:
                    subscript_numb_runs+=1 #increment count of times the subscript completely ran
                    if subscript_numb_runs < subscript_runthroughs: #if we are running the same subscript again
                        numb_subscript = 0 #start from the top
            elif numb_script < script_length: #if there are still main scriptcommands to execute
                if type(SCRIPT[numb_script]) == list: #coded out each argument
                    choice = SCRIPT[numb_script][0]
                    args = SCRIPT[numb_script][1]
                    if DEBUG_LOOP_PRINT:
                        print(str(loops) +': ' + str(CHOICE_STRING_MAP[choice]))
                else: #using the script_map shortcut
                    key = SCRIPT[numb_script]
                    if DEBUG_LOOP_PRINT:
                        print(str(loops) +': ' + str(key))
                    choice = GRID_SCRIPT_MAP[key][0]
                    args = GRID_SCRIPT_MAP[key][1]
                numb_script+=1
            else: #no scripted actions queued, user inputs their choice manually
                choice = int(input(GRID_TEST_MENU))

            #This can choose either update, or one of the other random action sets
            if choice == GRID_CHOICE_RANDOM_ACTION:
                choice, args = randomAction()

            if choice == GRID_CHOICE_RANDOM_CAMERA_ACTION:
                choice, args = randomCameraAction()

            if choice == GRID_CHOICE_RANDOM_SCENE_ACTION:
                choice, args = randomSceneAction()

            if choice == GRID_CHOICE_RANDOM_SPRITE_ACTION:
                choice, args = randomSpriteAction()

            if choice == GRID_CHOICE_QUIT:
                keep_going = False
                choice = GRID_CHOICE_NOP

            elif choice == GRID_CHOICE_EXEC:
                args = execCommand(*args)

            elif choice == GRID_CHOICE_UPDATE:
                update_count+=1
                if update_count in UPDATE_BREAK_POINTS:  # for handy breakpoints at specified script step(s)
                    print('At update break point:  ' + str(update_count))
                    #IS_RUN_TESTS = True
                update(game_engine_mock, update_count) #an update/render call
                if IS_RUN_TESTS and update_count >= TESTS_AFTER_UPDATE_CT:
                    runSceneTests(game_engine_mock, SCENE_TEST_COLLECTION)
                #checking conditions and running agent chaos is for a new run not a saved run
                if not IS_SAVED_RUN:
                    #use the TestConditionManager to check if all desired states were hit
                    if IS_CHECK_CONDITIONS:
                        if  not test_condition_manager.isMet():
                            if GRID_DEBUG_PRINT_FUNCTIONS:
                                print("Running Test Conditions")
                            test_condition_manager.testConditions(game_engine_mock)
                        elif QUIT_IF_CONDITIONS_MET:
                            keep_going = False
                        if PRINT_CONDITION_STATUS !=0 and (update_count) % PRINT_CONDITION_STATUS == 0:
                            print("\n\n")
                            print("Status update at update: ",(update_count))
                            print("Total loops: ",(loops))
                            test_condition_manager.printStatus()
                            print("\n\n")
                    if AGENT_CHAOS_RUN !=0 and (update_count) % AGENT_CHAOS_RUN == 0:
                        #We will save the update here, and also save the chaose
                        #on a script re-run, we will run the same chaos after the update
                        chaos_id, passing = agent_chaos.runNewChaos(game_engine_mock, SCENE_TEST_COLLECTION)
                        script_saver.appendCommand(choice, args)
                        script_saver.appendCommand(GRID_CHOICE_CHAOS, chaos_id)
                        choice = GRID_CHOICE_NOP
                        if not passing:
                            print("Agent Chaos failed to detect an error")
                            assert False

            elif choice == GRID_CHOICE_CHAOS:
                choice = GRID_CHOICE_NOP #Don't need to save Chaos on reruns
                if AGENT_CHAOS_RUN !=0:
                    passing = agent_chaos.runSavedChaos(game_engine_mock, args)
                    if not passing:
                        print("Agent Chaos rerun failed")
                        assert False

            elif choice == GRID_CHOICE_INSERT_SPRITE: #this will set the entity_id for next scripted calls to the newly created sprite
                inserted_entity_id, args = insertSprite(game_engine_mock, *args)
                if DEBUG_LOOP_PRINT:
                    print('New entity id: ' + str(inserted_entity_id))
                scene_id = args[0]
                if args[0] != 0: #this is signalling  NOP
                    game_engine_mock.addTestingEntityId(scene_id, inserted_entity_id)

            elif choice == GRID_CHOICE_REMOVE_SPRITE:
                args = removeSprite(game_engine_mock, *args)
                if args[0] != 0: #this is signalling  NOP
                    game_engine_mock.removeTestingEntityId(args[0])

            elif choice == GRID_CHOICE_PAN_SPRITE:
                args = panSprite(game_engine_mock, *args)

            elif choice == GRID_CHOICE_PAN_SPRITE_RANDOM:
                args = panSpriteRandom(game_engine_mock, *args)
                choice = GRID_CHOICE_PAN_SPRITE #now when we save the script, we will pan the same values

            elif choice == GRID_CHOICE_MOVE_SPRITE:
                args = moveSprite(game_engine_mock, *args)

            elif choice == GRID_CHOICE_MOVE_SPRITE_RANDOM:
                args = moveSpriteRandom(game_engine_mock, *args)
                choice = GRID_CHOICE_MOVE_SPRITE #now when we save the script, we will move the same values

            elif choice == GRID_CHOICE_FLIP_ANIMATION:
                args = flipAnimation(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_BEHAVIOR_STATE:
                args = setBehaviorState(game_engine_mock, *args)

            elif choice == GRID_CHOICE_PAN_CAMERA:
                args = panCamera(game_engine_mock, *args)

            elif choice == GRID_CHOICE_PAN_CAMERA_RANDOM:
                args = panCameraRandom(game_engine_mock)
                choice = GRID_CHOICE_PAN_CAMERA #now when we save the script, we will pan the same values

            elif choice == GRID_CHOICE_MOVE_CAMERA:
                args = moveCamera(game_engine_mock, *args)

            elif choice == GRID_CHOICE_MOVE_CAMERA_RANDOM:
                args = moveCameraRandom(game_engine_mock)
                choice = GRID_CHOICE_MOVE_CAMERA #now when we save the script, we will move the same values

            elif choice == GRID_CHOICE_LOAD_SCRIPT:
                SCRIPT, args = script_loader.loadScript(*args)
                numb_script = 0
                script_length = len(SCRIPT)
                choice = GRID_CHOICE_NOP #we just keep saving to the same script_file

            elif choice == GRID_CHOICE_LOAD_SUBSCRIPT:
                subscript, args = script_loader.loadSubscript(*args)
                numb_subscript = 0
                subscript_length = len(subscript)
                #default to run a subscript once, after loading the subscript can set it to run multiple times
                subscript_numb_runs = 0 #reset count of current subscript runs
                choice = GRID_CHOICE_NOP #prevents saving this action

            elif choice == GRID_CHOICE_SET_SCRIPT_RUNTHROUGHS:
                if args[0] is None: #manual call
                    subscript_runthroughs = setSubscriptRunthroughs(*args)
                else:
                    subscript_runthroughs = args[0]
                choice = GRID_CHOICE_NOP  # prevents saving this action

            elif choice == GRID_CHOICE_ACTIVATE_ENTITY:
                args = activateEntity(game_engine_mock, *args)

            elif choice == GRID_CHOICE_DEACTIVATE_ENTITY:
                args = deactivateEntity(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_ENTITY_ALWAYS_ACTIVE:
                args = setEntityAlwaysActive(game_engine_mock, *args)

            elif choice == GRID_CHOICE_REMOVE_ENTITY_ALWAYS_ACTIVE:
                args = removeEntityAlwaysActive(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_SPRITE_VISIBLE:
                args = setEntitySpriteVisible(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_SPRITE_INVISIBLE:
                args = setSpriteInvisible(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_SPRITE_ETHEREAL:
                args = setSpriteEthereal(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_SPRITE_TANGIBLE:
                args = setSpriteTangible(game_engine_mock, *args)

            elif choice == GRID_CHOICE_ACTIVATE_ENTITY_PHYSICS:
                args = activateEntityPhysics(game_engine_mock, *args)

            elif choice == GRID_CHOICE_DEACTIVATE_ENTITY_PHYSICS:
                args = deactivateEntityPhysics(game_engine_mock, *args)

            elif choice == GRID_CHOICE_ACTIVATE_ENTITY_BEHAVIOR:
                args = activateEntityBehavior(game_engine_mock, *args)

            elif choice == GRID_CHOICE_DEACTIVATE_ENTITY_BEHAVIOR:
                args = deactivateEntityBehavior(game_engine_mock, *args)

            elif choice == GRID_CHOICE_ACTIVATE_ENTITY_AI:
                args = activateEntityAi(game_engine_mock, *args)

            elif choice == GRID_CHOICE_DEACTIVATE_ENTITY_AI:
                args = deactivateEntityAI(game_engine_mock, *args)

            elif choice == GRID_CHOICE_ADD_ENTITY_DEPENDANT:
                args = addEntityDependancy(game_engine_mock, *args)

            elif choice == GRID_CHOICE_REMOVE_ENTITY_DEPENDANT:
                args = removeEntityDependancy(game_engine_mock, *args)

            elif choice == GRID_CHOICE_CONFIGURE_TESTS:
                args = configureTests(*args)
                if args[0] == 0:
                    IS_RUN_TESTS = False
                else:
                    IS_RUN_TESTS = True

            elif choice == GRID_CHOICE_ADD_SCENE:
                current_scene_id, args = createScene(game_engine_mock, *args)
                if current_scene_id == -1:
                    choice = GRID_CHOICE_NOP

            elif choice == GRID_CHOICE_REMOVE_SCENE:
                args = removeScene(game_engine_mock, *args)

            elif choice == GRID_CHOICE_ADD_LAYER:
                args = createSceneLayer(game_engine_mock, *args)

            elif choice == GRID_CHOICE_REMOVE_LAYER:
                args = removeSceneLayer(game_engine_mock, *args)

            #Called directly after GRID_CHOICE_ADD_SCENE to ensure a scene has a layer
            elif choice == GRID_CHOICE_ADD_LAYER_TO_CURRENT:
                if current_scene_id != -1:
                    args = createSceneLayer(game_engine_mock, current_scene_id, *args)
                    #when saving the scripted action, we have the scene ID saved in the args
                    #So change choice to a normal add layer, and we will use the same scene ID here
                    choice = GRID_CHOICE_ADD_LAYER
                else:
                    choice = GRID_CHOICE_NOP

            elif choice == GRID_CHOICE_ACTIVATE_SCENE:
                args = activateScene(game_engine_mock, *args)

            elif choice == GRID_CHOICE_DEACTIVATE_SCENE:
                args = deactivateScene(game_engine_mock, *args)

            elif choice == GRID_CHOICE_CREATE_CAMERA:
                current_camera_id, args = createCamera(game_engine_mock, *args)

            elif choice == GRID_CHOICE_REMOVE_CAMERA:
                args = removeCamera(game_engine_mock, *args)
                #This is to try and protect from attach cam to current using a removed camera id
                if args[0] == current_camera_id:
                    current_camera_id = 0 #0 will be treated as a NOP

            elif choice == GRID_CHOICE_ATTACH_CAMERA:
                args = attachCamera(game_engine_mock, *args)

            elif choice == GRID_CHOICE_DETACH_CAMERA:
                args = detachCamera(game_engine_mock, *args)

            elif choice == GRID_CHOICE_SET_CAMERA_SIZE:
                args = setCameraWindowSize(game_engine_mock, *args)

            elif choice == GRID_CHOICE_ATTACH_CAMERA_TO_CURRENT:
                if current_scene_id != -1:
                    args = attachCamera(game_engine_mock, current_scene_id, current_camera_id)
                    #In the script, we save it as a normal attach, which will use the above current values
                    choice = GRID_CHOICE_ATTACH_CAMERA
                else:
                    choice = GRID_CHOICE_NOP

            elif choice == GRID_CHOICE_RESET_ENGINE:
                resetGameEngine(game_engine_mock)
                current_entity_id = None

            #this creates a new folder and continues the script sequence from the next command on
            #if used before resetting game engine, can be used to start scripts from different points in execution
            #If used at a random juncture, won't get the same state, use it in conjuction with a reset engine
            elif choice == GRID_CHOICE_NEW_SEQUENCE:
                if DEBUG_LOOP_PRINT:
                    print("Starting next script sequnce: " + str(script_saver.script_sequence_number+1))
                script_saver.newScriptSequence()
                if REMOVE_PAST_SEQUENCE:
                    script_loader.setProtectDirectory(script_saver.getScriptFolder().replace("\\",""))
                    script_loader.scriptCleanup()
                choice = GRID_CHOICE_NOP  # prevents saving this action
                if AGENT_CHAOS_RUN:
                    #most likley don't care anymore if we got to this point, so trash existing chaos scripts
                    #the chaos scripts won't be deleted from trash until at least 1 more sequence
                    agent_chaos.trashCurrentScripts()

            elif choice == GRID_CHOICE_SET_LOAD_SCRIPT_PATH:
                args = script_loader.setScriptPath(*args)

            elif choice == GRID_CHOICE_NOP:
                print('this is here for a convenient breakpoint, or NOP ')

            if choice != GRID_CHOICE_NOP: #don't need to save nop's to our scripts
                script_saver.appendCommand(choice, args)

            if 0 < MAX_LOOPS <= loops or \
                    0 < MAX_UPDATES <= update_count: #0 means MAX is infinite
                keep_going = False

            if loops in LOOP_BREAK_POINTS: #for handy breakpoints at specified script step(s)
                print('At loop break point:  ' + str(loops))
                #if loops == 746500:
                #    print("test on")
                #    IS_RUN_TESTS = True

        except Exception as e:
            print("Exception at loop " + str(loops))
            print("Total updates: " + str(update_count))
            print(str(e))
            try:
                print("Choice and args:")
                print(str(choice))
                print(str(args))
            except Exception as e2:
                print("Failed to print the script choice/args")
                print(str(e2))
            try:
                if type(choice) is int and choice > 0 and choice != 9999:
                        if type(args) is list or type(args) is tuple:
                            script_saver.appendCommand(choice, args)
                            script_saver.saveScript()
            except Exception as e2:
                print("Exception, during save script action")
                print(str(e2))
            exceptions_caught+=1
            if 0 < MAX_EXCEPTIONS <= exceptions_caught: #0 means MAX is infinite
                keep_going = False
    try:
        script_saver.saveScript()
    except Exception as e:
        print('Unable to save script at end of test: ' + str(e))
    print("Total loops " + str(loops))
    print("Total updates: " + str(update_count))
    print("scene_layer_grid test end")
