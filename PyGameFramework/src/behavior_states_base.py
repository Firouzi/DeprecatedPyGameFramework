import sys
sys.path.append("parameters\\")
import TIMING_PARAM

class BehaviorStateBase:
    send_force = None  # func* to Physics
    send_sound = None  # func* to Sound
    send_event = None  # func* to Event
    get_position = None # func* to Physics

    def __init__(self,
                 entity_id, #int
                 layer_level_id, #int
                 subcomponent_index, #int
                 behavior_state_id, #const int
                 state_properties, #dict {string : <anything>}
                 behaviorFSMs): #*(BehaviorFSM,)
        self.entity_id = entity_id
        self.layer_level_id = layer_level_id
        self.subcomponent_index = subcomponent_index
        self.behavior_state_id = behavior_state_id
        self.behaviorFSMs = behaviorFSMs

        #animation timer
        self._animation_scaling_factor = 1.0 #speed up or slow down the animation
        self._current_timer_ms = 0 #int number of ms on current timer
        self._animation_loops = 0 #int - number of times the frames have gone back to index 0
        self._current_frame_index = 0 #int - which frame number we are on currenlty
        #Each entry is the number of ms for that frame.  The SpriteInstance will setup this list
        self._frame_times_ms = [500, 500, 500, 500] #placeholder value, will be updated by SpriteInstance
        self._numb_frames = 4 #placeholder value, will be updated by SpriteInstance

        #input
        self._key_state = dict() #every update loop these values are updated by inputhandler

        #properties
        #These properties describe the type of state this is - in the event where we only care about the general
        #type of state and not he unique state clasee
        self._state_properties = state_properties #{string : <anything>}

    def setAnimationScalingFactor(self,
                                  animation_scaling_factor):
        self._animation_scaling_factor = animation_scaling_factor

    #Returns false if this property exists, else the propery
    def getStateProperty(self,
                         property): #string
        if self._state_properties.get(property):
            return self._state_properties[property]
        return False

    def getCurrentFrameIndex(self): #animation frame
        return self._current_frame_index

    def setBehaviorStateFrameTimes(self,
                                   frame_times_ms): #(int,)
        self._frame_times_ms = tuple(frame_times_ms)
        self._numb_frames = len(frame_times_ms)

    def getBehaviorId(self):
        return self.behavior_state_id

    #Returns True if the timer wrapped around and increments timer_loops, else return False
    #This can be called by Child Classes on update for a standard increment
    #but it is not required to be called.  Can also be overridden
    def incrementTimer(self,
                       increment_amount): #int
        self._current_timer_ms += int(increment_amount * self._animation_scaling_factor) #default is BehaviorStateBase.MS_PER_UPDATE
        if self._current_timer_ms >= self._frame_times_ms[self._current_frame_index]:
            self._current_timer_ms = 0
            return self._updateFrameIndex() #returns True if the animation has wrapped
        return False

    def _updateFrameIndex(self):
        self._current_frame_index +=1
        if self._current_frame_index >= self._numb_frames:
            self._current_frame_index = 0
            self._animation_loops += 1
            return True # Timer wrapped around
        return False

    def resetTimer(self):
        self._current_timer_ms = 0
        self._current_frame_index = 0
        self._animation_loops = 0

    #update the timer and behavior here on each loop
    #Return -1 for no state transition, 0 for a pop, or a behavior_state_id
    def update(self):
        self.incrementTimer(TIMING_PARAM.MS_PER_UPDATE)
        return -1

    def enter(self):
        self.resetTimer()

    def exit(self):
        pass

    def updateControlInputState(self,
                                key_state):#{CONTROL_INPUT : Value}
        self._key_state = key_state

    #TODO might just add to a contact queue to be handled on upate
    def handleContact(self,
                      sender_component_id, #int
                      sender_subcomponent_index): #int
        pass
