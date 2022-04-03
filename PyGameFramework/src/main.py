import pygame
from time import time
import sys
sys.path.append("parameters\\")
import TIMING_PARAM


from debug import DebugHandler
import builder as game_engine_builder
from game_states import GameStateBase
def convertMilliseconds(seconds):
    return seconds/1000

def buildGameEngine(IS_DEBUGGER_RUN = False):
    builder = game_engine_builder.GameEngineBuilder()
    behavior_component_system = builder.buildBehaviorComponentSystem()
    debug_handler = DebugHandler()
    game_states = builder.buildGameStates()
    game_state_stack = builder.buildGameStateStack(game_states[0])
    input_manager = builder.buildInputManager(behavior_component_system, debug_handler)
    event_handler = builder.buildEventHandler(game_states[0])
    e_resource_manager = builder.buildEntityResourceManager()
    physics_component_system = builder.buildPhysicsComponentSystem()
    panorama_component_system = builder.buildPanoramaComponentSystem()
    tilemap_component_system = builder.buildTilemapComponentSystem()
    sprite_image_manager = builder.buildSpriteImageManager()
    sprite_component_system = builder.buildSpriteComponentSystem()
    s_resource_manager = builder.buildSceneResourceManager()
    window = builder.buildWindow()
    scene_handler = builder.buildSceneHandler(window)

    builder.setupBehaviorState(event_handler, physics_component_system)
    builder.setupComponent(scene_handler)
    builder.setupCamera(scene_handler)
    builder.setupEntityResourceManager(sprite_image_manager.loadSpriteData, sprite_component_system,
                                    physics_component_system, behavior_component_system)
    builder.setupGameStates(s_resource_manager, e_resource_manager, scene_handler,
                         physics_component_system, behavior_component_system, sprite_component_system)
    builder.setupPanoramaComponentSystem()
    builder.setupResourceManager(scene_handler.addSceneComponent)
    builder.setupRenderLayer()
    builder.setupSpriteClasses(physics_component_system, behavior_component_system)
    builder.setupSceneLayer()
    builder.setupSceneResourceManager(sprite_image_manager.loadPanoramaImage, sprite_image_manager.loadAtlasImage,
                                      scene_handler.createSceneLayer, panorama_component_system, tilemap_component_system)
    builder.setupSceneHandler()
    builder.setupTilemapComponentSystem()

    game_engine = GameEngine(game_states = game_states,
                             starting_game_state = game_states[0],
                             game_state_stack = game_state_stack,
                             behavior_component_system = behavior_component_system,
                             physics_component_system = physics_component_system,
                             sprite_component_system = sprite_component_system,
                             panorama_component_system = panorama_component_system,
                             tilemap_component_system = tilemap_component_system,
                             scene_resource_manager= s_resource_manager,
                             entity_resource_manager= e_resource_manager,
                             sprite_image_manager = sprite_image_manager,
                             event_handler = event_handler,
                             input_manager = input_manager,
                             debug_handler = debug_handler,
                             scene_handler= scene_handler,
                             #IS_DEBUGGER_RUN= IS_DEBUGGER_RUN) #TODO hardcode test
                             IS_DEBUGGER_RUN = True)
    GameStateBase.call_exit_game = game_engine.exitGame

    builder.setupDebugHandler(game_engine)
    return game_engine

class GameEngine:
    def __init__(self,
                 game_states,  #[GameStateBase]
                 starting_game_state,  #*GameStateBase
                 game_state_stack,  #StateStack
                 behavior_component_system,  #BehaviorComponentSystem
                 physics_component_system,  #PhysicsComponentSystem
                 sprite_component_system,  #SpriteComponentSystem
                 panorama_component_system,  #PanoramaComponentSysten
                 tilemap_component_system,
                 entity_resource_manager,  #EntityResourceManager
                 scene_resource_manager,  #SceneResourceManager
                 sprite_image_manager,  #SpriteImageManager
                 event_handler,  #EventHandler
                 input_manager,  #InputManager
                 debug_handler,  #DebugHandler
                 scene_handler,  #SceneHandler
                 IS_DEBUGGER_RUN = False): #True if running with debugger

        #Game State
        self.game_states = game_states
        self.game_state_stack = game_state_stack
        self.current_game_state = starting_game_state
        self._IS_DEBUGGER_RUN = IS_DEBUGGER_RUN

        #Component Systems
        self._behavior_component_system = behavior_component_system
        self._physics_component_system = physics_component_system
        self._sprite_component_system = sprite_component_system
        self._panorama_component_system = panorama_component_system
        self._tilemap_component_system = tilemap_component_system

        #Managers and Handlers
        self._entity_resource_manager = entity_resource_manager
        self._scene_resource_manager = scene_resource_manager
        self._sprite_image_manager = sprite_image_manager
        self._event_handler = event_handler
        self._input_manager = input_manager
        self._debug_handler = debug_handler
        #Graphics and Sound
        self._scene_handler = scene_handler

        #Game Parameters (generally concrete)
        self._time_scaling_factor = 1.0 #slow/speed gameplay: 10.0 = 10x FASTER
        self._ms_per_update = convertMilliseconds(TIMING_PARAM.MS_PER_UPDATE) #convert int:5 to float:.005
        #Debug purposes only
        self.isPaused = False #This pauses almost all of the engine functionality

    def gameloop(self):
        keep_going = True
        previous_loop_time = time()
        lag = 0
        self.addhammer(500) #TODO hardcode test
        while keep_going:
            current_loop_time = time()
            elapsed_loop_time = current_loop_time - previous_loop_time
            previous_loop_time = current_loop_time

            #TODO - removed during optimization testing
            # Prevents freezing game after pausing in debugger mode
            #if self._IS_DEBUGGER_RUN:
            #    if elapsed_loop_time > convertMilliseconds(100):
            #        elapsed_loop_time = convertMilliseconds(15)
            #by using the scaling factor, the game components update the same time step
            #but they will do it at a rate determined by _time_scaling_factor
            #lag += elapsed_loop_time*self._time_scaling_factor

            lag = .016 #TODO Hardcode test
            while lag >= self._ms_per_update:
                #Still update the inputs, even when paused
                self._input_manager.handleInput()
                if not self.isPaused:
                    # processAI() #Maybe not every loop
                    self._behavior_component_system.update()
                    #animation timers handled in panorama/tilemap systems
                    self._panorama_component_system.update()
                    self._tilemap_component_system.update()
                    #bvc.update()
                    self._physics_component_system.update()
                    #hud.update()
                    self._event_handler.update()
                lag -= self._ms_per_update
            #sprite is not in the main update loop because the timer is handled by behavior_component
            self._sprite_component_system.update()
            lag_normalized = lag / TIMING_PARAM.MS_PER_UPDATE * self._time_scaling_factor
            assert(lag_normalized<1)
            self._scene_handler.render(lag_normalized = lag_normalized)
            self.handleDebug()
            exit_event = pygame.event.get(pygame.QUIT)
            if exit_event:
                self.exitGame()
                self._event_handler.exitEvent()

    def stateTransition(self,
                        game_state_index): #int
        self.current_game_state.exit()
        if game_state_index == 0:
            game_state_index = self.game_state_stack.pop()
        else:
            self.game_state_stack.push(game_state_index)
        self.current_game_state = self.game_states[game_state_index]
        self.current_game_state.enter()

    def exitGame(self):
        sys.exit()

    #To start a debug console, hit the ` key.
    #To make the debugger active, hit d (won't run the console statements if inactive)
    def handleDebug(self):
        self._debug_handler.update()
        if self._debug_handler.isActive():
            self.debugRunExec()

    def debugRunExec(self):
        exec_statement = ''
        while self._debug_handler.hasNext():
            try:
                exec_statement = self._debug_handler.next()
                exec(exec_statement)
            except Exception as e:
                print('Exception caught while running exec:')
                print('Exec Statement: ' + str(exec_statement))
                print(e)
            sys.stdout.flush()

    #Press the +/- keys to change game speed
    #Not using a mutex lock because debugger only calls this from it's receive input method
    #Note that slowing the game speed a lot makes it harder to register input
    #Render is still called, but update loops happen more/less pending speed
    def debugChangeGameSpeed(self,
                             amount): #float
        self._time_scaling_factor += amount
        if self._time_scaling_factor <= 0.01:
            self._time_scaling_factor = 0.01

    #prevent all update loops from running
    def pause(self):
        self.isPaused = not self.isPaused

    #TODO - debug quick load a new entity
    def adde(self, tag_id = 0, initial_pos = (100,100), e_resource_id = 1000, layer_level_id = 2):
        self._event_handler.adde(tag_id, initial_pos, e_resource_id, layer_level_id)

    #TODO - debug remove an entity
    def removee(self, component_element_id):
        self._event_handler.removee(component_element_id = component_element_id)

    #TODO - debug quick load many new entiy's
    def addhammer(self, numb, start_pos = (50,50)):
        i = 0
        while i < numb:
            self.adde(0, (start_pos[0]+i*30, start_pos[1]+i*30))
            i+=1

    #TODO - debug quick remove many entiy's
    def removehammer(self, range):
        i = range[0]
        while i <= range[1]:
            self.removee(i)
            i+=1


if __name__ == "__main__":
    pygame.init()
    #if we pass in a command line argument, we run the gameloop in debug mode
    #in debug mode, the game loop has a fixed amount of updates per loop regardless of real clock
    SET_IS_DEBUGGER_RUN = False
    if len(sys.argv)>1: #TODO - make this a specific string!
        SET_IS_DEBUGGER_RUN = True
    print('Building Engine...')
    game_engine_instance = buildGameEngine(SET_IS_DEBUGGER_RUN)
    print('Starting Main Loop')
    game_engine_instance.gameloop()
    print('Ending Program')


