from component_system import EntityComponentSystem, EntityComponent, Subcomponent
from game_states import StateStack
from behavior_states import BehaviorStateFactory
from utility import Ptr
import sys
sys.path.append("parameters\\")
import FUNCTIONAL_PARAM

class BehaviorStatePtr(Ptr):
    def __init__(self, obj):
        super(BehaviorStatePtr, self).__init__(obj = obj,
                                               ptr_id = 0, #don't care
                                               free_callback = None) #don't care
    def update(self):
        return self._obj.update()
    def updateControlInputState(self, key_state):
        self._obj.updateControlInputState(key_state = key_state)
    def exit(self):
        self._obj.exit()
    def enter(self):
        self._obj.enter()
    def getBehaviorId(self):
        return self._obj.getBehaviorId()
    def getFrameTimer(self):
        return self._obj.getFrameTimer()
    def getStateProperty(self, property):
        return self._obj.getStateProperty(property)

class BehaviorFSM(Subcomponent):
    def __init__(self,
                 parent_component,
                 component_element_id,  #int
                 layer_level_id, #int
                 subcomponent_index,  #int
                 behavior_states,  #{behavior_state_id : BehaviorState}
                 initial_state_id): #int
        super(BehaviorFSM, self).__init__(parent_component = parent_component,
                                          component_element_id=component_element_id,
                                          layer_level_id = layer_level_id,
                                          subcomponent_index = subcomponent_index)
        self.behavior_states = behavior_states #A Dictionary of all the possible states this FSM can be in
        #A ptr that we can update with the current state,
        #this wrapper allows all objects always to refer to current_behavior_state even when the FSM changes states
        self.current_behavior_state = BehaviorStatePtr(behavior_states[initial_state_id])
        self.behavior_state_stack = StateStack(initial_state = self.current_behavior_state.getBehaviorId(),
                                               max_size = FUNCTIONAL_PARAM.MAX_BEHAVIOR_STATES)

        self.key_state = dict() #to be updated by inputHandler

    def update(self):
        #We need the latest inputs before we update the behavior
        self.current_behavior_state.updateControlInputState(key_state = self.key_state)
        behavior_state_id = self.current_behavior_state.update()
        if behavior_state_id >= 0: #state transition
            self.current_behavior_state.exit()
            if behavior_state_id == 0:
                behavior_state_id = self.behavior_state_stack.pop()
            else:
                self.behavior_state_stack.push(behavior_state_id)
            self.current_behavior_state.set(self.behavior_states[behavior_state_id])
            #The new state needs to update it's inputs
            self.current_behavior_state.updateControlInputState(key_state=self.key_state)
            self.current_behavior_state.enter()

    #This is updated during the input handling step
    def updateControlInputState(self,
                                key_state):# {CONTROL_INPUT : Bool}
        self.key_state = key_state

    def handleContact(self, #TODO - might just pass on the contact to be queued
                      sender_component_id, #int
                      sender_subcomponent_index): #int
        new_state_id = self.current_behavior_state.get().handleContact(sender_component_id, sender_subcomponent_index)
        if new_state_id != 0:
            self.current_behavior_state.exit()
            self.current_behavior_state.set(self.behavior_states[new_state_id])
            self.current_behavior_state.enter()

    def getFrameTimer(self):
        return self.current_behavior_state.getFrameTimer()

    def getBehaviorId(self):
        return self.current_behavior_state.getBehaviorId()

    def getStateProperty(self,
                         property):
        return self.current_behavior_state.getStateProperty(property = property)

    def setBehaviorStateFrameTimes(self,
                                   behavior_state_id, #int
                                   frame_times_ms): #[int]
        try:
            self.behavior_states[behavior_state_id].setBehaviorStateFrameTimes(frame_times_ms = frame_times_ms)
        except:
            assert(1==2)

    def setBehaviorState(self,
                         behavior_state_id, #int
                         is_exit, #bool
                         is_enter): #bool
        if self.behavior_states.get(behavior_state_id) is not None:
            if is_exit:
                self.current_behavior_state.exit()
            self.behavior_state_stack.push(behavior_state_id)
            self.current_behavior_state.set(self.behavior_states[behavior_state_id])
            if is_enter:
                self.current_behavior_state.enter()

class EntityBehaviorComponent(EntityComponent):
    def __init__(self,
                 entity_element_id,  #int
                 layer_level_id, #int
                 behavior_FSMs): #(behavior_FSM,)
        super(EntityBehaviorComponent, self).__init__(entity_element_id = entity_element_id,
                                                      layer_level_id = layer_level_id)
        self._behavior_FSMs = behavior_FSMs
        #This is a list of BehaviorStatePtr's, which correspond 1:1 to the Subcomponent BehaviorFSM's
        self._current_behavior_states = list() #[BehaviorStatePtr]

    #Doesn't need to do anything since the Ptr's in the subcomponent are not part of a PtrPool
    #This object will be removed from the ComponentSystem
    def kill(self):
        pass

    #Needs to be called before behavior states are requested
    def initialize(self):
        self._behavior_FSMs = tuple(self._behavior_FSMs)
        self._current_behavior_states = list() #redundant but needed to mask false warning from PyCharm
        for behavior_FSM in self._behavior_FSMs:
            self._current_behavior_states.append(behavior_FSM.current_behavior_state)
        self._current_behavior_states = tuple(self._current_behavior_states)

    def setBehaviorStateFrameTimes(self,
                                   behavior_FSM_index, #int
                                   behavior_state_id, #int
                                   frame_times_ms): #[int]
        self._behavior_FSMs[behavior_FSM_index].setBehaviorStateFrameTimes(behavior_state_id = behavior_state_id,
                                                                           frame_times_ms = frame_times_ms)

    def setBehaviorState(self,
                         behavior_FSM_index, #int
                         behavior_state_id, #int
                         is_exit, #bool
                         is_enter): #bool
        self._behavior_FSMs[behavior_FSM_index].setBehaviorState(behavior_state_id = behavior_state_id,
                                                                 is_exit = is_exit,
                                                                 is_enter = is_enter)

    def getBehaviorStates(self):
        return self._current_behavior_states

    def getBehaviorState(self,
                         behavior_FSM_index): #int
        return self._behavior_FSMs[behavior_FSM_index].current_behavior_state

    def update(self):
        for behavior_FSM in self._behavior_FSMs:
            behavior_FSM.update()

    def updateControlInputState(self,
                                key_state):  #{CONTROL_INPUT : Bool}
        for behavior_FSM in self._behavior_FSMs:
            behavior_FSM.updateControlInputState(key_state = key_state)

    def handleContact(self,
                      behavior_FSM_index, #int
                      sender_component_id, #int
                      sender_subcomponent_index): #int
        self._behavior_FSMs[behavior_FSM_index].handleContact(sender_component_id, sender_subcomponent_index)

    def getFrameTimer(self, behavior_FSM_index):
        return self._behavior_FSMs[behavior_FSM_index].getFrameTimer()

    def getBehaviorFsmId(self,
                         behavior_FSM_index): #int
        return self._behavior_FSMs[behavior_FSM_index].getBehaviorStateId()


class BehaviorComponentSystem(EntityComponentSystem):
    def __init__(self):
        super(BehaviorComponentSystem, self).__init__()

        self.behavior_state_factory = BehaviorStateFactory()
        self._entity_behavior_components = dict()#{int : component}
        self.received_contacts_queue = list() #[int]

    def removeComponent(self,
                        component_element_id): #int
        try:
            self._entity_behavior_components[component_element_id].kill() #TODO - does nothing, not needed?
            del self._entity_behavior_components[component_element_id]
            return True
        except:
            return False

    def setBehaviorStateFrameTimes(self,
                                   entity_id, #int
                                   behavior_FSM_index, #int
                                   behavior_state_id, #int
                                   frame_times_ms): #(int,)
        try:
            self._entity_behavior_components[entity_id].setBehaviorStateFrameTimes(behavior_FSM_index = behavior_FSM_index,
                                                                                   behavior_state_id = behavior_state_id,
                                                                                   frame_times_ms = frame_times_ms)
        except:
            assert(1==2)

    def setBehaviorState(self,
                         entity_id, #int
                         behavior_FSM_index, #int
                         behavior_state_id, #int
                         is_exit, #bool
                         is_enter): #bool
        try:
            self._entity_behavior_components[entity_id].setBehaviorState(behavior_FSM_index = behavior_FSM_index,
                                                                         behavior_state_id = behavior_state_id,
                                                                         is_exit = is_exit,
                                                                         is_enter = is_enter)
        except:
            assert(1==2)

    def getBehaviorState(self,
                         entity_id, #int
                         behavior_FSM_index): #int
        return self._entity_behavior_components[entity_id].getBehaviorState(
            behavior_FSM_index = behavior_FSM_index)

    def updateControlInputState(self,
                                entity_id,  #int
                                key_state):  # {CONTROL_INPUT : Bool}
        try:
            self._entity_behavior_components[entity_id].updateControlInputState(key_state = key_state)
            return True
        except:
            return False

    def receiveContact(self,
                       receiver_entity_id, #int
                       receiver_behavior_FSM_index, #int
                       sender_component_id, #int
                       sender_subcomponent_index): #int
        self.received_contacts_queue.append((receiver_entity_id,
                                             receiver_behavior_FSM_index,
                                             sender_component_id,
                                             sender_subcomponent_index))

    def processContacts(self):
        for contact in self.received_contacts_queue:
            if self._entity_behavior_components.get(contact[0]) is not None:
                self._entity_behavior_components[contact[0]].handleContact( #call entity_id handle()
                    contact[1], #receiver_behavior_FSM_index
                    contact[2], #sender_component_id
                    contact[3]) #sender_subcomponent_index
        self.received_contacts_queue.clear()

    def getFrameTimer(self,
                      entity_id, #int
                      behavior_FSM_index): #int
        try:
            return self._entity_behavior_components[entity_id].getFrameTimer(behavior_FSM_index)
        except:
            assert(1==2)

    def getBehaviorStateId(self,
                           entity_id,  # int
                           behavior_FSM_index):  # int
        try:
            return self._entity_behavior_components[entity_id].getBehaviorFsmId(behavior_FSM_index)
        except:
            assert(1==2)

    def createComponent(self,
                        component_element_id,  #int
                        layer_level_id, #int
                        resource_data): #ResourceData
        behaviorFSMs = list() #each behavior state gets a pointer to this
        #Create the Component first because subcomponents need the referene
        entity_behavior_component = EntityBehaviorComponent(
            entity_element_id= component_element_id,
            layer_level_id = layer_level_id,
            behavior_FSMs = behaviorFSMs)
        subcomponent_index = 0
        #1 list of states for each subcomponent
        for behavior_state_id_list in resource_data.behavior_state_id_lists:
            #create all of the subcomponents behavior states
            behavior_states = dict()
            for behavior_state_id in behavior_state_id_list:
                behavior_states[behavior_state_id] = \
                    self.behavior_state_factory.createBehaviorState(entity_id = component_element_id,
                                                                    layer_level_id = layer_level_id,
                                                                    subcomponent_index = subcomponent_index,
                                                                    behavior_state_id = behavior_state_id,
                                                                    behaviorFMS = behaviorFSMs)#behaviorFSMs is a ref
            #create the FSM and pass in the created states
            behaviorFSMs.append(BehaviorFSM(parent_component = entity_behavior_component,
                                            component_element_id=component_element_id,
                                            layer_level_id = layer_level_id,
                                            subcomponent_index= subcomponent_index,
                                            behavior_states = behavior_states,
                                            #the val for the initial state of each FSM is indexed relative to subcomponent index
                                            initial_state_id = resource_data.initial_behavior_state_ids[subcomponent_index]))
            subcomponent_index+=1
        entity_behavior_component.initialize()
        self._entity_behavior_components[component_element_id] = entity_behavior_component

    def getBehaviorStates(self,
                          component_element_id): #int
        try:
            return self._entity_behavior_components[component_element_id].getBehaviorStates()
        except:
            return tuple()

    def update(self):
        for entity_behavior_component in self._entity_behavior_components.values():
            entity_behavior_component.update()
