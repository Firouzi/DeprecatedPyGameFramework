from Test_condition_manager import TestConditionContainer, TestCondition
from Sprite_state import SpriteStateEnum

class StateTransitionContainer(TestConditionContainer):
    def __init__(self, node_test_conditions):
        super(StateTransitionContainer, self).__init__(node_test_conditions)
        #transition TO this state
        self.name = "Node State Transition Container"

        #{id: previous state}
        self.state_map = dict()

        #node_test_conditions
        #we will have a clone_condition with nested dependant condition for EACH
        #{from state: to state}

        #{SPRITE_STATE_ACTIVE :
        #       {
        #           SPRITE_STATE_ACTIVE : (test_conditions for clones/dependants)
        #           SPRITE_STATE_ACTIVE_INVISIBLE : (test_conditions for clones/dependants)
        #           SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE : (test_conditions for clones/dependants)
        #           etc...
        #       }
        #SPRITE_STATE_ACTIVE_INVISIBLE :
        #       {
        #           SPRITE_STATE_ACTIVE : (test_conditions for clones/dependants)
        #           SPRITE_STATE_ACTIVE_INVISIBLE : (test_conditions for clones/dependants)
        #           SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE : (test_conditions for clones/dependants)
        #           etc...
        #       }
        #}

    def printStatus(self):
        print(self.name,": Status:")
        if self.isMet():
            print("All conditions met")
            return
        print("Unmet conditions for following transitions")
        for from_state, to_states in self.test_conditions.items():
            for to_state, test_conditions in to_states.items():
                print("FROM state '", from_state, "', TO state '",to_state,"'")
                #Printing every condition is tooooo long
                #for test_condition in test_conditions:
                #    test_condition.printStatus()

    def isMet(self):
        #we track any of the transitions that are completely met, and remove them to be efficient in checking conditions
        remove_list = list() #[(SPRITE_STATE, SPRITE_STATE)]
        all_met = True
        if not self.is_met:
            for from_state, to_states in self.test_conditions.items():
                for to_state, test_conditions in to_states.items():
                    all_to_states_met = True
                    for test_condition in test_conditions:
                        if not test_condition.isMet():
                            all_to_states_met = False
                            all_met = False
                            break
                    if all_to_states_met:
                        remove_list.append((from_state, to_state))
        for remove in remove_list:
            try:
                del(self.test_conditions[remove[0]][remove[1]])
                if len(self.test_conditions[remove[0]]) == 0:
                    del(self.test_conditions[remove[0]])
            except Exception as e:
                print("Exception caught running test condition")
                print("e")
        if all_met:
            self.all_met = True
            return True
        return False

    def runContainer(self, game_engine):
        for active_scene in game_engine._scene_manager._active_scenes.values():
            self._testNodes(active_scene._sprites)

    def _testNodes(self, nodes):
        for entity_id, node in nodes.items():
            if self.state_map.get(entity_id) is None:
                #just add it to the state map this time, do not check for a condition
                current_state = node.current_sprite_state.sprite_state_enum
                self.state_map[entity_id] = current_state
            else:
                previous_state = self.state_map[entity_id]
                current_state = node.current_sprite_state.sprite_state_enum
                from_state_conditions = self.test_conditions.get(previous_state)
                if from_state_conditions is not None:
                    to_state_conditions = from_state_conditions.get(current_state)
                    if to_state_conditions is not None:
                        for test_condition in to_state_conditions:
                            if not test_condition.isMet():
                                test_condition.testCondition(node)


#Look for conditions a node is in based on it's state
class NodeStateConditionContainer(TestConditionContainer):
    def __init__(self, node_test_conditions, node_state_enum):
        super(NodeStateConditionContainer, self).__init__(node_test_conditions)
        self.node_state_enum = node_state_enum
        self.name = "Node State Container - " + str(node_state_enum)


    #params should be a list of sprites, or do you break that out at this point?
    def runContainer(self, game_engine):
            for active_scene in game_engine._scene_manager._active_scenes.values():
                self._testNodes(active_scene._sprites)

    #pass a list of nodes to test. Might be multiple calls to this since nodes may be in discrete lists
    def _testNodes(self, nodes):
        #for each node that matches this containers state, see if it meets any of our conditions
        for entity_id, node in nodes.items():
            if node.current_sprite_state.sprite_state_enum == self.node_state_enum:
                for node_test_condition in self.test_conditions:
                    if not node_test_condition.isMet():
                        node_test_condition.testCondition(node)

class CloneCondition(TestCondition):
    def __init__(self, test_conditions, num_clones): #[hclones, vclones] (either 0, 1 or 2. 2 implies any amount > 1
        super(CloneCondition, self).__init__(test_conditions)
        self.num_clones = num_clones
        self.name = "Clone Condition - " + str(num_clones)

    #checks if passed in node meets the desired number of clones
    def selfTest(self, node):
        hclone_count = 0
        vclone_count = 0
        hmet = False
        vmet = False
        #count number of clones sprite has
        if node.horizontal_clone is not None:
            hclone_count +=1
            if node.horizontal_clone.horizontal_clone is not None:
                hclone_count+=1
        if node.vertical_clone is not None:
            vclone_count +=1
            if node.vertical_clone.vertical_clone is not None:
                vclone_count+=1
        #check if the number matches the clones we want
        if self.num_clones[0] == 0:
            if hclone_count == 0:
                hmet = True
        elif self.num_clones[0] == 1:
            if hclone_count == 1:
                hmet = True
        else:
            if hclone_count>1:
                hmet = True
        if self.num_clones[1] == 0:
            if vclone_count == 0:
                vmet = True
        elif self.num_clones[1] == 1:
            if vclone_count == 1:
                vmet = True
        else:
            if vclone_count>1:
                vmet = True
        if vmet and hmet:
            return True
        return False

class DependentCondition(TestCondition):
    def __init__(self, test_conditions, num_dependants): # 0, 1, >1
        super(DependentCondition, self).__init__(test_conditions)
        self.num_dependants = num_dependants
        self.name = "Dependent Condition - " + str(num_dependants)

    #checks if passed in node meets the desired number of dependants
    def selfTest(self, node):
        count = 0
        count += len(node.dependant_sprite_nodes)
        count += len(node.inactive_dependants)
        if self.num_dependants == 0 or self.num_dependants == 1:
            if count == self.num_dependants:
                return True
        else:
            if count > 1:
                return True
        return False

#returns list of all combination of CloneConditions
def _buildCloneConditions():
    clone_test_conditions = list()
    for hclone in range(3):
        for vclone in range(3):
            for dep in range(3):
                clone_test_conditions.append(CloneCondition([DependentCondition(None, dep)], (hclone, vclone)))
    #clone_test_conditions.append(CloneCondition(None,(0,0)))
    return clone_test_conditions

#returns a list of all dependant conditions, with a clone condition of 0,0
def _buildDependentConditions():
    dependent_test_conditions = list()
    for dep in range(3):
        clone_condition = CloneCondition(None, [0,0])
        dependent_test_conditions.append(DependentCondition([clone_condition],dep))
    #dependent_test_conditions.append(DependentCondition(None,0))
    return dependent_test_conditions

def buildNodeTransitionContainer():
    containers = list()
    #double iterate through this list to create a dict lookup of every state transition
    enum_list = (SpriteStateEnum.SPRITE_STATE_ACTIVE,
                 SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE,
                 SpriteStateEnum.SPRITE_STATE_ACTIVE_ETHEREAL,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL,
                 #invisible ethereals do not have clones
                 SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL,
                 SpriteStateEnum.SPRITE_STATE_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_INVISIBLE_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_ETHEREAL_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED,
                 SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED,
                 )

    #don't look for clones in the following to_states
    no_clones_states = (
        SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL,
        SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL,
        SpriteStateEnum.SPRITE_STATE_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_INVISIBLE_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_ETHEREAL_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED,
        SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED,
    )

    test_condition_dict = dict()

    for from_state in enum_list:
        test_condition_dict[from_state] = dict()
        for to_state in enum_list:
            if to_state in no_clones_states:
                test_condition_dict[from_state][to_state] = _buildDependentConditions()
            else:
                test_condition_dict[from_state][to_state] = _buildCloneConditions()

    state_transition_container = StateTransitionContainer(test_condition_dict)
    containers.append(state_transition_container)
    return containers

#return a list of all sprite_state test containers
def buildNodeStateContainers():
    containers = list()
    containers.append(NodeStateConditionContainer(_buildCloneConditions(), SpriteStateEnum.SPRITE_STATE_ACTIVE))
    containers.append(NodeStateConditionContainer(_buildCloneConditions(), SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE))
    containers.append(NodeStateConditionContainer(_buildCloneConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE))
    containers.append(NodeStateConditionContainer(_buildCloneConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE))
                                                #note: deactivated nodes do not have clones
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_INVISIBLE_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildCloneConditions(), SpriteStateEnum.SPRITE_STATE_ACTIVE_ETHEREAL))
    containers.append(NodeStateConditionContainer(_buildCloneConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL))
                                                # note: invisible ethereal nodes do not have clones
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ACTIVE_INVISIBLE_ETHEREAL))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ETHEREAL_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_INVISIBLE_ETHEREAL_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_ETHEREAL_DEACTIVATED))
    containers.append(NodeStateConditionContainer(_buildDependentConditions(), SpriteStateEnum.SPRITE_STATE_ALWAYS_ACTIVE_INVISIBLE_ETHEREAL_DEACTIVATED))
    return containers