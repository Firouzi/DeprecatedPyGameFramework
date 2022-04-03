from input_handler import ENTITY_CONTROL_INPUT, CAMERA_CONTROL_INPUT
from behavior_states_base import BehaviorStateBase
import sys
sys.path.append("parameters\\")
import TIMING_PARAM

#Unique IDs - To keep the ID's easier to define in the JSON, we will apply the MASK in the factory
BEHAVIORSTATEID_NULL = 0
BEHAVIORSTATEID_PARENT_IDLE1 = 1
BEHAVIORSTATEID_PARENT_IDLE2 = 2
BEHAVIORSTATEID_PARENT_MOVE1 = 3
BEHAVIORSTATEID_PARENT_MOVE2 = 4
BEHAVIORSTATEID_CHILD_IDLE1 = 5
BEHAVIORSTATEID_CHILD_IDLE2 = 6
BEHAVIORSTATEID_CHILD_MOVE = 7

BEHAVIORSTATEID_CAMERA = 15

STATE_PROPERTIES_MOTION = {"in_motion" :  True}
STATE_PROPERTIES_NONE = dict()

#TODO - probably move factory to it's own page eventually as it will grow like crazy
class BehaviorStateFactory:
    def __init__(self):
        pass

    #We are applying the state masks here, so the unique ID is all that is passed in
    def createBehaviorState(self,
                            entity_id, #int
                            layer_level_id, #int
                            subcomponent_index, #int
                            behavior_state_id, #int
                            behaviorFMS): #*[BehaviorFMS]
        if behavior_state_id == BEHAVIORSTATEID_NULL:
            return BehaviorNullState(entity_id = entity_id,
                                     layer_level_id = layer_level_id,
                                     subcomponent_index = subcomponent_index,
                                     behavior_state_id = BEHAVIORSTATEID_NULL,
                                     state_properties = STATE_PROPERTIES_NONE,
                                     behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_PARENT_IDLE1:
            return ParentIdle1(entity_id = entity_id,
                               layer_level_id=layer_level_id,
                               subcomponent_index = subcomponent_index,
                               behavior_state_id=BEHAVIORSTATEID_PARENT_IDLE1,
                               state_properties=STATE_PROPERTIES_NONE,
                               behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_PARENT_IDLE2:
            return ParentIdle2(entity_id = entity_id,
                               layer_level_id=layer_level_id,
                               subcomponent_index = subcomponent_index,
                               behavior_state_id=BEHAVIORSTATEID_PARENT_IDLE2,
                               state_properties=STATE_PROPERTIES_NONE,
                               behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_PARENT_MOVE1:
            return ParentMove1(entity_id = entity_id,
                               layer_level_id=layer_level_id,
                               subcomponent_index = subcomponent_index,
                               behavior_state_id=BEHAVIORSTATEID_PARENT_MOVE1,
                               state_properties=STATE_PROPERTIES_MOTION,
                               behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_PARENT_MOVE2:
            return ParentMove2(entity_id = entity_id,
                               layer_level_id=layer_level_id,
                               subcomponent_index = subcomponent_index,
                               behavior_state_id=BEHAVIORSTATEID_PARENT_MOVE2,
                               state_properties=STATE_PROPERTIES_MOTION,
                               behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_CHILD_IDLE1:
            return ChildIdle1(entity_id = entity_id,
                              layer_level_id=layer_level_id,
                              subcomponent_index = subcomponent_index,
                              behavior_state_id=BEHAVIORSTATEID_CHILD_IDLE1,
                              state_properties=STATE_PROPERTIES_NONE,
                              behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_CHILD_IDLE2:
            return ChildIdle2(entity_id = entity_id,
                              layer_level_id=layer_level_id,
                              subcomponent_index = subcomponent_index,
                              behavior_state_id=BEHAVIORSTATEID_CHILD_IDLE2,
                              state_properties=STATE_PROPERTIES_NONE,
                              behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_CHILD_MOVE:
            return ChildMove(entity_id = entity_id,
                             layer_level_id=layer_level_id,
                             subcomponent_index = subcomponent_index,
                             behavior_state_id=BEHAVIORSTATEID_CHILD_MOVE,
                             state_properties=STATE_PROPERTIES_MOTION,
                             behaviorFSMs = behaviorFMS)
        elif behavior_state_id == BEHAVIORSTATEID_CAMERA:
            return CameraIdle(entity_id = entity_id,
                              layer_level_id=layer_level_id,
                              subcomponent_index = subcomponent_index,
                              behavior_state_id=BEHAVIORSTATEID_CAMERA,
                              state_properties=STATE_PROPERTIES_NONE,
                              behaviorFSMs = behaviorFMS)

#The 'do nothing' state
class BehaviorNullState(BehaviorStateBase):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id,
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(BehaviorNullState, self).__init__(entity_id = entity_id,
                                                layer_level_id = layer_level_id,
                                                subcomponent_index = subcomponent_index,
                                                behavior_state_id = behavior_state_id,
                                                state_properties = state_properties,
                                                behaviorFSMs = behaviorFSMs)

class CameraIdle(BehaviorStateBase):
    observer_methods = list() #receive methods from any that need the offsets

    def __init__(self,
                 entity_id,  # int
                 layer_level_id,
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs):  # *[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(CameraIdle, self).__init__(entity_id = entity_id,
                                         layer_level_id = layer_level_id,
                                         subcomponent_index = subcomponent_index,
                                         behavior_state_id = behavior_state_id,
                                         state_properties=state_properties,
                                         behaviorFSMs = behaviorFSMs)

        self.move_speed = 1.0
        self._allow_control = False
        self._debounce_allow_control = False #TODO - handle with diff states?

    #Sends force to physics based on input. Returns True if force is !=0, else False
    def handleMovement(self):
        force = [0.0, 0.0, 0.0]

        if self._allow_control:
            if self._key_state.get(CAMERA_CONTROL_INPUT.PAN_UP):
                force[1] -= self.move_speed
            if self._key_state.get(CAMERA_CONTROL_INPUT.PAN_RIGHT):
                force[0] += self.move_speed
            if self._key_state.get(CAMERA_CONTROL_INPUT.PAN_DOWN):
                force[1] += self.move_speed
            if self._key_state.get(CAMERA_CONTROL_INPUT.PAN_LEFT):
                force[0] -= self.move_speed

        if self._debounce_allow_control: #Waiting to release the key
            if not self._key_state.get(CAMERA_CONTROL_INPUT.TOGGLE_CONTROL):
                self._debounce_allow_control = False
        else: #Waiting for the key press
            if self._key_state.get(CAMERA_CONTROL_INPUT.TOGGLE_CONTROL):
                self._debounce_allow_control = True
                self._allow_control = not self._allow_control

        if force[0] != 0 or force[1] != 0 or force[1] !=0:
            BehaviorStateBase.send_force(entity_id = self.entity_id,
                                         particle_index = self.subcomponent_index,
                                         force = force)
            return True
        else:
            return False

    def update(self):
        #TODO = follow player character here
        camera_move = self.handleMovement()
        if camera_move: #update the renderer's offset if the camera has moved
            camera_position = BehaviorStateBase.get_position(entity_id = self.entity_id,
                                                             particle_index = self.subcomponent_index)
            self.sendOffsets(camera_position)
        return -1

    def sendOffsets(self,
                    offsets): #[int, int]
        for observer_method in CameraIdle.observer_methods:
            observer_method(offsets)



class ParentIdle1(BehaviorStateBase):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id,
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ParentIdle1, self).__init__(entity_id = entity_id,
                                          layer_level_id = layer_level_id,
                                          subcomponent_index = subcomponent_index,
                                          behavior_state_id = behavior_state_id,
                                          state_properties=state_properties,
                                          behaviorFSMs = behaviorFSMs)
        self.move_speed = 1.0
        self._loop_wraps = 10 #number of animations before change state
        self._transition_state = BEHAVIORSTATEID_PARENT_IDLE2

    #Sends force to physics based on input. Returns True if force is !=0, else False
    def handleMovement(self):
        force = [0.0, 0.0, 0.0]

        #handle each key press
        if self._key_state.get(ENTITY_CONTROL_INPUT.MOVE_UP):
            force[1] -= self.move_speed
        if self._key_state.get(ENTITY_CONTROL_INPUT.MOVE_RIGHT):
            force[0] += self.move_speed
        if self._key_state.get(ENTITY_CONTROL_INPUT.MOVE_DOWN):
            force[1] += self.move_speed
        if self._key_state.get(ENTITY_CONTROL_INPUT.MOVE_LEFT):
            force[0] -= self.move_speed
        if self._key_state.get(ENTITY_CONTROL_INPUT.ACTION):
            pass

        if force[0] != 0 or force[1] != 0 or force[1] !=0:
            BehaviorStateBase.send_force(entity_id = self.entity_id,
                                         particle_index = self.subcomponent_index,
                                         force = force)
            return True
        else:
            return False

    def update(self):
        timer_wrapped = self.incrementTimer(TIMING_PARAM.MS_PER_UPDATE)
        is_moving = self.handleMovement()

        #Transition to moving state if we started moving
        if is_moving:
            return BEHAVIORSTATEID_PARENT_MOVE1

        #Go to the next idle state animation if here long enough
        if timer_wrapped and self._animation_loops >= self._loop_wraps:
            return self._transition_state

        return -1 #No state transition

class ParentIdle2(ParentIdle1):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id, #int
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ParentIdle2, self).__init__(entity_id = entity_id,
                                          layer_level_id = layer_level_id,
                                          subcomponent_index = subcomponent_index,
                                          behavior_state_id = behavior_state_id,
                                          state_properties=state_properties,
                                          behaviorFSMs = behaviorFSMs)
        self._loop_wraps = 5
        self._transition_state = BEHAVIORSTATEID_PARENT_IDLE1

class ParentMove1(ParentIdle1):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id, #int
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ParentMove1, self).__init__(entity_id = entity_id,
                                          layer_level_id = layer_level_id,
                                          subcomponent_index = subcomponent_index,
                                          behavior_state_id = behavior_state_id,
                                          state_properties=state_properties,
                                          behaviorFSMs = behaviorFSMs)

    def update(self):
        timer_wrapped = self.incrementTimer(TIMING_PARAM.MS_PER_UPDATE)
        is_moving = self.handleMovement()

        #Back to idle 1 if we aren't moving
        if not is_moving:
            return BEHAVIORSTATEID_PARENT_IDLE1

        #Go to the next state if we looped the timer enough times
        if timer_wrapped and self._animation_loops >= 3:
            return BEHAVIORSTATEID_PARENT_MOVE2

        return -1 #No state transition

class ParentMove2(ParentIdle1):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id, #int
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ParentMove2, self).__init__(entity_id = entity_id,
                                          layer_level_id = layer_level_id,
                                          subcomponent_index = subcomponent_index,
                                          behavior_state_id = behavior_state_id,
                                          state_properties=state_properties,
                                          behaviorFSMs = behaviorFSMs)
        #Moves faster!
        self.move_speed = 2.0

    def update(self):
        self.incrementTimer(TIMING_PARAM.MS_PER_UPDATE)
        is_moving = self.handleMovement()

        #Back to idle 1 if we aren't moving
        if not is_moving:
            return BEHAVIORSTATEID_PARENT_IDLE1

        return -1 #No state transition



class ChildIdle1(BehaviorStateBase):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id,
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ChildIdle1, self).__init__(entity_id = entity_id,
                                         layer_level_id = layer_level_id,
                                         subcomponent_index = subcomponent_index,
                                         behavior_state_id = behavior_state_id,
                                         state_properties=state_properties,
                                         behaviorFSMs = behaviorFSMs)
        self.transition_state = BEHAVIORSTATEID_CHILD_IDLE2
        self.animation_loops_max = 2

    def update(self):
        #If we are on the move, change to move state
        if self.behaviorFSMs[0].getStateProperty("in_motion"):
            return BEHAVIORSTATEID_CHILD_MOVE

        timer_wrapped = self.incrementTimer(TIMING_PARAM.MS_PER_UPDATE)
        if timer_wrapped and self._animation_loops >= self.animation_loops_max:
            #we want to reset only when transitioning between the idle states
            self.resetTimer()
            return self.transition_state
        return-1

    #we will maintain our place in the loop
    def enter(self):
        pass


#Same update behavior as ChildIdle1, just change the transition_state and animation speed
class ChildIdle2(ChildIdle1):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id,
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ChildIdle2, self).__init__(entity_id = entity_id,
                                         layer_level_id = layer_level_id,
                                         subcomponent_index = subcomponent_index,
                                         behavior_state_id = behavior_state_id,
                                         state_properties=state_properties,
                                         behaviorFSMs = behaviorFSMs)
        self.transition_state = BEHAVIORSTATEID_CHILD_IDLE1
        self.animation_loops_max = 5

class ChildMove(BehaviorStateBase):
    def __init__(self,
                 entity_id,  # int
                 layer_level_id, #int
                 subcomponent_index,  # int
                 behavior_state_id,  # const int
                 state_properties,  # dict {string : <anything>}
                 behaviorFSMs): #*[BehaviorFSM] - ptrs to all behaviorFSMs for this component
        super(ChildMove, self).__init__(entity_id = entity_id,
                                        layer_level_id = layer_level_id,
                                        subcomponent_index = subcomponent_index,
                                        behavior_state_id = behavior_state_id,
                                        state_properties=state_properties,
                                        behaviorFSMs = behaviorFSMs)

    def update(self):
        #POP back to the last idle state animation
        if not self.behaviorFSMs[0].getStateProperty("in_motion"):
            return 0

        self.incrementTimer(TIMING_PARAM.MS_PER_UPDATE)
        return -1

