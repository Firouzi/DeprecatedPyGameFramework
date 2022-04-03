from enum import Enum

class EVENT_TYPE(Enum):
    LOAD_SCENE = 1
    SPAWN_ENTITY = 2
    PLAY_SOUND = 3
    PAUSE_GAME = 4
    UNPAUSE_GAME = 5
    REMOVE_ENTITY = 6
    EXIT_EVENT = 7

class GameEvent:
    def __init__(self,
                 startup_delay_ms, #int
                 ending_delay_ms, #int
                 is_parallel, #boolean
                 event_type): #EVENT_TYPE
        self.startup_delay_ms = startup_delay_ms
        self.ending_delay_ms = ending_delay_ms
        #If true, can go on to the next event in the sequence even if there is a startup delay invoked
        self.is_parallel = is_parallel
        self.event_type = event_type

class EventExit(GameEvent):
    def __init__(self,
                 startup_delay_ms, #int
                 ending_delay_ms, #int
                 is_parallel): #boolean
        super(EventExit, self).__init__(startup_delay_ms = startup_delay_ms,
                                        ending_delay_ms = ending_delay_ms,
                                        is_parallel = is_parallel,
                                        event_type = EVENT_TYPE.EXIT_EVENT)

class EventRemoveEntity(GameEvent):
    def __init__(self,
                 startup_delay_ms, #int
                 ending_delay_ms, #int
                 is_parallel, #boolean
                 component_element_id): #int
        super(EventRemoveEntity, self).__init__(startup_delay_ms = startup_delay_ms,
                                                ending_delay_ms = ending_delay_ms,
                                                is_parallel = is_parallel,
                                                event_type = EVENT_TYPE.REMOVE_ENTITY)
        #This ID is dynamically generated by the resource_manager
        #This ID is unique to 1 entity, and shared across all components/subcomponents of that entity
        self.component_element_id = component_element_id

class EventSpawnEntity(GameEvent):
    def __init__(self,
                 startup_delay_ms,  #int
                 ending_delay_ms,  #int
                 is_parallel,  #boolean
                 e_resource_collection_id,  #int
                 e_tag_id,  #int - that the can be used to locate specific known entites
                 layer_level_id,  #int
                 initial_position,  #[int, int, int]
                 initial_velocity,  #[int, int, int]
                 initial_acceleration,  #[int, int, int]
                 initial_orientation,  #[float, float]
                 initial_behavior_states): #[int]
        super(EventSpawnEntity, self).__init__(startup_delay_ms = startup_delay_ms,
                                               ending_delay_ms = ending_delay_ms,
                                               is_parallel = is_parallel,
                                               event_type = EVENT_TYPE.SPAWN_ENTITY)
        self.e_resource_collection_id = e_resource_collection_id
        self.e_tag_id = e_tag_id
        self.layer_level_id = layer_level_id
        self.initial_position = initial_position
        self.initial_velocity = initial_velocity
        self.initial_acceleration = initial_acceleration
        self.initial_orientation = initial_orientation
        #if initial_behavior_states is None, stay with resource default init state
        #If a list of ints, we have the starting state for each component
        self.initial_behavior_states = initial_behavior_states

class EventLoadScene(GameEvent):
    def __init__(self,
                 startup_delay_ms,  #int
                 ending_delay_ms,  #int
                 is_parallel,  #boolean
                 gamescene_resource_id,  #[int]
                 s_tag_ids):  # int - that the can be used to locate specific known layers or scene_components
        super(EventLoadScene, self).__init__(startup_delay_ms = startup_delay_ms,
                                             ending_delay_ms = ending_delay_ms,
                                             is_parallel = is_parallel,
                                             event_type = EVENT_TYPE.LOAD_SCENE)
        self.gamescene_resource_id = gamescene_resource_id

        #The element IDs are returned in this format from a spawnScene:
        #{layer_level_id_1: [component_id1, component_id2,...], layer_level_id_2 : [component_id1, component_id2,...],...}
        #To designate tags: The dict key represents each layer to make tags for
        #Each entry is a list of pairs (index, tagvalue)  EG:
        #{4 : [0,52, 12,496], 8: [3, 3001]}
        #   - layer_level 4 has 2 tags; the 0th component as "52", and the 12th component as "496".
        #   - layer_level 8 has 1 tag; the 3rd component as "3001'
        self.s_tag_ids = s_tag_ids

class EventHandler:
    def __init__(self,
                 current_game_state): #*GameEngine.current_game_state
        self.current_game_state = current_game_state
        self.event_queue = list() #[GameEvent]
        self.current_events = list() #[*GameEvent]

        self.game_state_transition = None #func* to GameEngine state transition

        event_load_scene = EventLoadScene(startup_delay_ms = 0,
                                          ending_delay_ms = 0,
                                          is_parallel = False,
                                          gamescene_resource_id = 100,
                                          s_tag_ids = {0 : [0, 1500]}) #arbitrarily tag the Panorama as 1500

        #debug add event to the queue
        event_spawn_player = EventSpawnEntity(startup_delay_ms = 0,
                                              ending_delay_ms = 0,
                                              is_parallel = False,
                                              e_resource_collection_id= 1000,  #1000 is PC id
                                              e_tag_id = 1000,  #We will use 1000 for player 1
                                              layer_level_id = 2,
                                              initial_position = [100,200,0],
                                              initial_velocity = [0,0,0],
                                              initial_acceleration = [0,0,0],
                                              initial_orientation = [0.0, 0.0],
                                              initial_behavior_states = None)

        event_spawn_npc = EventSpawnEntity(startup_delay_ms = 0,
                                           ending_delay_ms = 0,
                                           is_parallel = False,
                                           e_resource_collection_id= 1000,
                                           e_tag_id = 0,  #0 means 'No tag'
                                           layer_level_id= 2,
                                           initial_position = [290,280,0],
                                           initial_velocity = [0,0,0],
                                           initial_acceleration = [0,0,0],
                                           initial_orientation = [0.0, 0.0],
                                           initial_behavior_states = [2,5])

        event_spawn_camera = EventSpawnEntity(startup_delay_ms = 0,
                                              ending_delay_ms = 0,
                                              is_parallel = False,
                                              e_resource_collection_id= 0,  #0 is the camera entity
                                              e_tag_id= 1,  #1 is camera tag
                                              layer_level_id= 2,
                                              initial_position = [0,0,0],
                                              initial_velocity = [0,0,0],
                                              initial_acceleration = [0,0,0],
                                              initial_orientation = [0.0, 0.0],
                                              initial_behavior_states = None)

        self.receiveEvent(event_load_scene)
        self.receiveEvent(event_spawn_player)
        self.receiveEvent(event_spawn_camera)
        self.receiveEvent(event_spawn_npc)

    def update(self):
        for event in self.event_queue:
            new_game_state_index = self.current_game_state.handleEvent(event)
            if new_game_state_index >= 0:
                self.game_state_transition(new_game_state_index)

        self.event_queue.clear() #TODO - DEBUG, won't be clearing this


    def receiveEvent(self,
                     game_event): #GameEvent
        self.event_queue.append(game_event)

    #Trigger exit event was triggered, add the exit_event to the FRONT of the queue
    def exitEvent(self):
        event_exit = EventExit(startup_delay_ms = 0,
                               ending_delay_ms = 0,
                               is_parallel = False)
        self.event_queue.insert(0, event_exit)


    #TODO debug quick add entity
    def adde(self, tag_id, initial_pos, e_resource_id, layer_level_id):
        initial_position = [initial_pos[0], initial_pos[1], 0] #hard code Z=0 for convenience
        event_spawn_npc = EventSpawnEntity(startup_delay_ms = 0,
                                           ending_delay_ms = 0,
                                           is_parallel = False,
                                           e_resource_collection_id= e_resource_id,
                                           e_tag_id = tag_id,
                                           layer_level_id= layer_level_id,
                                           initial_position = initial_position,
                                           initial_velocity = [0,0,0],
                                           initial_acceleration = [0,0,0],
                                           initial_orientation = [0.0, 0.0],
                                           initial_behavior_states = [2,5])
        self.receiveEvent(event_spawn_npc)

    #TODO debug quick remove entity
    def removee(self, component_element_id):
        event_remove_entity = EventRemoveEntity(startup_delay_ms = 0,
                                                ending_delay_ms = 0,
                                                is_parallel = False,
                                                component_element_id = component_element_id)
        self.receiveEvent(event_remove_entity)