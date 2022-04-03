from Test_condition_manager import TestConditionManager
from Node_test_condition import buildNodeStateContainers, buildNodeTransitionContainer
from Scene_test_condition import buildSceneStateContainers

#TODO - finalize this list
def buildTestConditionManager():
    condition_containers = list()
    #condition_containers += buildNodeStateContainers()
    condition_containers += buildNodeTransitionContainer()
    #condition_containers += buildSceneStateContainers()
    test_condition_manager = TestConditionManager(condition_containers)
    return test_condition_manager