from event_handler import EVENT_TYPE


NO_STATE_TRANSITION = -1

#this can be used in any class which needs a statestack
#Acts as a circular buffer, rolling when it's length reaches max_states
class StateStack:
    def __init__(self,
                 initial_state, #state (type varies by use of class)
                 max_size): #int
        self._initial_state = initial_state
        self._max_size = max_size
        self._stack = list()
        self._current_index = 0
        self._has_wrapped = False
        self._init_stack()


    def push(self, state):
        self._current_index += 1
        #if we need to wrap around the circular buffer
        if self._current_index == self._max_size:
            self._current_index = 0
            self._has_wrapped = True

        self._stack[self._current_index] = state

    def pop(self):
        #If we have never wrapped the stack, we don't want to go backwards to the end
        #Those states have never really been pushed, so just stay at the beginning
        self._current_index -=1
        if self._current_index < 0:
            if self._has_wrapped:
                self._current_index = self._max_size -1
            else:
                self._current_index = 0

        return self._stack[self._current_index]

    #Set every starting state as the initial state (placeholder state)
    def _init_stack(self):
        self._stack = list()
        self._current_index = 0
        self._has_wrapped = False # If have never wrapped buffer, then when pop'd won't wrap backwards
        count = 0
        while count < self._max_size:
            self._stack.append(self._initial_state)
            count+=1

    def clearStack(self):
        self._init_stack()

class GameStateBase:
    #system functions
    call_exit_game = None #(GameEngine.exitGame())

    #any of the GameState children can call these by "GameStateBase.<functionname>(<args>)"
    call_spawn_entity = None #(e_resource_id : int)
    call_spawn_scene = None #(gamescene_resource_id : int)

    #remove entity
    #A list of func ptrs to removeComponent() methods, call them all to remove an entity completely
    call_remove_component_list = None #[ComponentSystem.removeComponent(component_element_id : int)]

    #set physics values
    call_set_entity_position = None #(entity_id : int, position : [int,int,int]
    call_set_entity_velocity = None  # (entity_id : int, position : [int,int,int]
    call_set_entity_acceleration = None  # (entity_id : int, position : [int,int,int]
    call_set_entity_orientation = None  # (entity_id : int, position : [int,int,int]

    #tag
    call_set_entity_tag = None #(element_id : int, e_tag_id : int)
    call_set_scene_tag = None #(element_id : int, s_tag_id : int)

    # (entity_id : int, behavior_FSM_index : int, behavior_state_id : int, is_exit : bool, is_enter : bool)
    call_set_behavior_state = None

    game_states = list() #[*GameState] a List of pointers to all game states for state transitions

    def __init__(self):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    #This function is NOT overriden in child classes
    def handleEvent(self,
                    game_event): #GameEvent
        if game_event.event_type == EVENT_TYPE.LOAD_SCENE:
            return self.handleLoadScene(game_event)
        elif game_event.event_type == EVENT_TYPE.SPAWN_ENTITY:
            return self.handleSpawnEntity(game_event)
        elif game_event.event_type == EVENT_TYPE.REMOVE_ENTITY:
            return self.handleRemoveEntity(game_event)
        elif game_event.event_type == EVENT_TYPE.PLAY_SOUND:
            return self.handlePlaySound(game_event)
        elif game_event.event_type == EVENT_TYPE.EXIT_EVENT:
            return self.handlePauseGame(game_event)
        elif game_event.event_type == EVENT_TYPE.PAUSE_GAME:
            return self.handleExitGame(game_event)
        elif game_event.event_type == EVENT_TYPE.UNPAUSE_GAME:
            return self.handleUnPauseGame(game_event)
        else:
            exit("GameStateBase received an uknown event type: " + str(game_event.event_type))


#The handle functions can be overwritten in child classes per desired state behavior
#return value is the index of the new state if applicable, or -1 for no transition
    def handleLoadScene(self,
                        game_event): #GameEvent
        scene_element_ids =  GameStateBase.call_spawn_scene(game_event.gamescene_resource_id)
        #Set the tag_ids
        for layer_level_id, s_tag_ids in game_event.s_tag_ids.items():
            index = 0
            while index < len(s_tag_ids):
                element_id_index = game_event.s_tag_ids[layer_level_id][index]
                element_id = scene_element_ids[layer_level_id][element_id_index]
                tag_id = game_event.s_tag_ids[layer_level_id][index+1]
                tag_success = GameStateBase.call_set_scene_tag(element_id = element_id,
                                                               tag_id = tag_id)
                if not tag_success:
                    print("tag may have failed for tag " + str(tag_id) +
                          " on element " + str(element_id))
                index +=2

        return NO_STATE_TRANSITION

    #calls remove component on all of the EntityComponentSystems
    def handleRemoveEntity(self,
                           game_event): #EventRemoveEntity
        for call_remove_component in GameStateBase.call_remove_component_list:
            call_remove_component(game_event.component_element_id)

        return NO_STATE_TRANSITION

    def handleSpawnEntity(self,
                          game_event): #EventSpawnEntity
        element_id = GameStateBase.call_spawn_entity(e_resource_collection_id = game_event.e_resource_collection_id,
                                                     layer_level_id = game_event.layer_level_id)
        GameStateBase.call_set_entity_position(entity_id = element_id,
                                               position = game_event.initial_position)
        GameStateBase.call_set_entity_velocity(entity_id = element_id,
                                               velocity = game_event.initial_velocity)
        GameStateBase.call_set_entity_acceleration(entity_id = element_id,
                                                   acceleration = game_event.initial_acceleration)
        GameStateBase.call_set_entity_orientation(entity_id = element_id,
                                                  orientation = game_event.initial_orientation)

        if game_event.initial_behavior_states is not None: #else stick with default initial
            behavior_FSM_index = 0
            for initial_behavior_state in game_event.initial_behavior_states:
                self.call_set_behavior_state(entity_id = element_id,
                                             behavior_FSM_index = behavior_FSM_index,
                                             behavior_state_id = initial_behavior_state,
                                             is_exit = False,
                                             is_enter = False)
                behavior_FSM_index +=1

        #If we have assigned a tag_id to this entity, set it here
        if game_event.e_tag_id != 0 :
            tag_success = GameStateBase.call_set_entity_tag(element_id = element_id,
                                                            tag_id =game_event.e_tag_id)
            if not tag_success:
                print("tag may have failed for tag " + str(game_event.e_tag_id) + " on element " + str(element_id))

        return NO_STATE_TRANSITION

    def handlePlaySound(self,
                        game_event): #GameEvent
        return NO_STATE_TRANSITION

    #We need to call the sys.exit from the main module or else pygame keeps a'runnin
    def handleExitGame(self,
                       game_event): #GameEvent
        GameStateBase.call_exit_game()

    def handlePauseGame(self,
                        game_event): #GameEvent
        return NO_STATE_TRANSITION

    def handleUnPauseGame(self,
                        game_event): #GameEvent
        return NO_STATE_TRANSITION

#Example
class GameStateChild(GameStateBase):
    def __init__(self):
        super(GameStateChild, self).__init__()

    #example ovverides
    def enter(self):
        pass

    def exit(self):
        pass

    def handleLoadScene(self,
                        game_event): #GameEvent
        return -1