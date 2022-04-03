#Ref UML Diagram InputHandler
import pygame
from enum import Enum

class CONTROL_INPUT(Enum):
    pass

#TODO - I think we need to refresh the keystate every time the handler becomes active
#TODO - If the handler is inacive, then active again, the key state could change in-between
class InputHandler:
    def __init__(self,
                 component_id, #int
                 is_active, #bool
                 is_blocking, #bool
                 is_consumer, #bool
                 input_map, #{pygame.input : CONTROL_INPUT}
                 key_state, #{CONTROL_INPUT : Bool}
                 send_input, #func*
                 successor): #Pointer to another InputHandler or NULL
        self.component_id = component_id #the component for which the inputs affect
        self.is_active = is_active #handle inputs if true
        self.is_blocking = is_blocking #pass unhandled inputs to successor if false
        self.is_consumer = is_consumer #consume mapped inputs if true
        self.input_map = input_map
        self.key_state = key_state
        #BehaviorComponentSystem.updateControlInputState(entity_id : int, key_state : {CONTROL_INPUT : Bool}
        self.send_input = send_input
        self.successor = successor #InputHandler

        #get the state of all keys.  If the key is in the input_map, set the keystate
        keys = pygame.key.get_pressed()
        for key in range(0, len(keys)):
            if self.input_map.get(key):
                self.key_state[self.input_map[key]] = keys[key] == 1
        #once first created, we send the initial state
        #After this, we can just update the keys when they have change events fired
        self.send_input(entity_id = component_id,
                        key_state = self.key_state)

    def handleInput(self,
                    keydown_events,  # [pygame.event.KEYDOWN]
                    keyup_events,  # [pygame.event.KEYUP]
                    joystick_axis_values):  # [float]
        unhandled_keydown_events = list()
        unhandled_keyup_events = list()
        unhandled_joystick_axis_values = list() #TODO
        keystate_has_changed = False
        if self.is_active:
            for keydown_event in keydown_events:
                if self.input_map.get(keydown_event.key) is not None:
                    control_input = self.input_map[keydown_event.key]
                    self.key_state[control_input] = True
                    keystate_has_changed = True
                else:
                    unhandled_keydown_events.append(keydown_event)
            for keyup_event in keyup_events:
                if self.input_map.get(keyup_event.key) is not None:
                    control_input = self.input_map[keyup_event.key]
                    self.key_state[control_input] = False
                    keystate_has_changed = True
                else:
                    unhandled_keyup_events.append(keyup_event)
            #TODO joysticks
            if keystate_has_changed:
                self.send_input(entity_id = self.component_id,
                                key_state = self.key_state)
        else:
            unhandled_keydown_events = keydown_events
            unhandled_keyup_events = keyup_events
            unhandled_joystick_axis_values = joystick_axis_values
        if not self.is_blocking and self.successor is not None:
            if self.is_consumer:
                self.successor.handleInput(keydown_events = unhandled_keydown_events,
                                           keyup_events = unhandled_keyup_events,
                                           joystick_axis_values = unhandled_joystick_axis_values)
            else:
                self.successor.handleInput(keydown_events = keydown_events,
                                           keyup_events = keyup_events,
                                           joystick_axis_values = keyup_events)

class InputManager:
    def __init__(self,
                 input_handlers): #[InputHandler]
        self._input_handlers = input_handlers

        self.joysticks = list()
        self.initializeJoysticks()

    def initializeJoysticks(self):
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            joystick.init()

    def handleInput(self):
        keydown_events = pygame.event.get(pygame.KEYDOWN)
        keyup_events = pygame.event.get(pygame.KEYUP)
        pygame.event.clear()
        joystick_axis_values = list()
        for joystick in self.joysticks:
            num_axes = joystick.get_numaxes()
            count = 0
            while count < num_axes:
                axes_value = joystick.get_axis(count)
                if -0.1 < axes_value > 0.1 or axes_value < -0.1:
                    joystick_axis_values.append(axes_value)
                else:
                    joystick_axis_values.append(0.0)
                count+=1

        self._input_handlers[0].handleInput(keydown_events = keydown_events,
                                            keyup_events = keyup_events,
                                            joystick_axis_values = joystick_axis_values)

#### Test Objects ####
class DEBUGGER_CONTROL_INPUT(CONTROL_INPUT):
    START_CONSOLE = 1
    TOGGLE_ACTIVE = 2
    SPEED_UP = 3
    SLOW_DOWN = 4
    PAUSE = 5

class CAMERA_CONTROL_INPUT(CONTROL_INPUT):
    PAN_UP = 1
    PAN_RIGHT = 2
    PAN_DOWN = 3
    PAN_LEFT = 4
    TOGGLE_CONTROL = 5

class ENTITY_CONTROL_INPUT(CONTROL_INPUT):
    MOVE_UP = 1
    MOVE_RIGHT = 2
    MOVE_DOWN = 3
    MOVE_LEFT = 4
    ACTION = 5

debugger_input_map = {pygame.K_BACKQUOTE : DEBUGGER_CONTROL_INPUT.START_CONSOLE, #` (lower case ~ key AKA BACKQUOTE)
                      pygame.K_d : DEBUGGER_CONTROL_INPUT.TOGGLE_ACTIVE, #d
                      pygame.K_KP_MINUS: DEBUGGER_CONTROL_INPUT.SLOW_DOWN, # -
                      pygame.K_SPACE : DEBUGGER_CONTROL_INPUT.PAUSE, # SPACE BAR
                      pygame.K_KP_PLUS : DEBUGGER_CONTROL_INPUT.SPEED_UP} # +

camera_input_map = {pygame.K_s : CAMERA_CONTROL_INPUT.PAN_UP,
                    pygame.K_c : CAMERA_CONTROL_INPUT.PAN_RIGHT,
                    pygame.K_x : CAMERA_CONTROL_INPUT.PAN_DOWN,
                    pygame.K_z : CAMERA_CONTROL_INPUT.PAN_LEFT,
                    pygame.K_a : CAMERA_CONTROL_INPUT.TOGGLE_CONTROL}

entity_input_map = {pygame.K_UP : ENTITY_CONTROL_INPUT.MOVE_UP,
                    pygame.K_RIGHT : ENTITY_CONTROL_INPUT.MOVE_RIGHT,
                    pygame.K_DOWN : ENTITY_CONTROL_INPUT.MOVE_DOWN,
                    pygame.K_LEFT : ENTITY_CONTROL_INPUT.MOVE_LEFT,
                    pygame.K_RETURN : ENTITY_CONTROL_INPUT.ACTION, }  #ENTER KEY

debug_key_state = {DEBUGGER_CONTROL_INPUT.START_CONSOLE : False,
                   DEBUGGER_CONTROL_INPUT.TOGGLE_ACTIVE : False}

camera_key_state = {CAMERA_CONTROL_INPUT.PAN_UP : False,
                    CAMERA_CONTROL_INPUT.PAN_RIGHT : False,
                    CAMERA_CONTROL_INPUT.PAN_DOWN : False,
                    CAMERA_CONTROL_INPUT.PAN_LEFT : False,
                    CAMERA_CONTROL_INPUT.TOGGLE_CONTROL : False}

entity_key_state = {ENTITY_CONTROL_INPUT.MOVE_UP : False,
                    ENTITY_CONTROL_INPUT.MOVE_RIGHT : False,
                    ENTITY_CONTROL_INPUT.MOVE_DOWN : False,
                    ENTITY_CONTROL_INPUT.MOVE_LEFT : False,
                    ENTITY_CONTROL_INPUT.ACTION : False}

















