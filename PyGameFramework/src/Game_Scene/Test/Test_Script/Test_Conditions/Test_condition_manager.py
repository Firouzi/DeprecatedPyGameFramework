"""
The purpose of this module is to define a checklist of states that we desire to hit during a test run.

"""

#TODO - state transition condition checker?
    #Would need to store entity id and status, and look for change from stat->stat
        #create a lookup table of all status transitions
    #TODO - include with clones and dependants as well
    #Note - if there were multiple transitions within an update, it could not be perfect (but close enough)


class TestConditionManager:
    def __init__(self, condition_containers):
        self.condition_containers = condition_containers
        self.is_met = False

    def testConditions(self, game_engine):
        try:
            for condition_container in self.condition_containers:
                if condition_container.isRunContainer():
                    condition_container.runContainer(game_engine)
        except Exception as e:
            print("Exception caught running test condition")
            print("e")

    def isMet(self):
        if not self.is_met:
            for condition_container in self.condition_containers:
                if not condition_container.isMet():
                    return False
            print("All test conditions were met")
            self.is_met = True
        return True

    def printStatus(self):
        print("*** Test Conditions Status ***")
        if self.is_met:
            print("Test conditions are all met.")
        else:
            print("Some test conditions not met. Printing status of unmet containers...")
            for condition_container in self.condition_containers:
                condition_container.printStatus()

    #reset all conditions to False (perhaps we want to achieve them all within 1 engine reset)
    def resetAll(self):
        self.is_met = False
        for condition_container in self.condition_containers:
            condition_container.resetAll()

#We want to hit all test_conditions for this state
class TestConditionContainer:
    def __init__(self, test_conditions, name = "Test Condition Container"):
        self.test_conditions = test_conditions
        self.is_met = False
        self.name = name

    #The first time this is called after the conditions are met, we enter the loop
    #When they are met, the loop will set is_met to True. Then on, we just return True
    def isMet(self):
        if not self.is_met:
            for test_condition in self.test_conditions:
                if not test_condition.isMet():
                    return False
            self.is_met = True
        return True

    #reset all conditions to False (perhaps we want to achieve them all within 1 engine reset)
    def resetAll(self):
        self.is_met = False
        for test_condition in self.test_conditions:
            test_condition.resetAll()

    def printStatus(self):
        if not self.is_met:
            print("Unmet conditions in Container: ", self.name)
            print("Printing unmet conditions...")
            for test_condition in self.test_conditions:
                test_condition.printStatus()

    def isRunContainer(self):
        return not self.isMet()

    def runContainer(self, game_engine):
        pass

class TestCondition:
    def __init__(self, test_conditions, name = "Test Condition"): #can have nested conditions, or None
        self.test_conditions = test_conditions
        self.is_met = False
        self.name = name

    #reset all conditions to False (perhaps we want to achieve them all within 1 engine reset)
    def resetAll(self):
        self.is_met = False
        for test_condition in self.test_conditions:
            test_condition.resetAll()

    def setIsMet(self, is_met):
        self.is_met = is_met

    def isMet(self):
        return self.is_met

    #First check nested condition(s)
    def testSubConditions(self, params):
        sub_conditions_met =  True
        if self.test_conditions is not None:
            for test_condition in self.test_conditions:
                if test_condition.testCondition(params):
                    test_condition.setIsMet(True)
                else:
                    sub_conditions_met = False
                    break
        return sub_conditions_met

    #If any condition fails, reset everything to not met
    def resetSubConditions(self):
        if self.test_conditions is not None:
            for test_condition in self.test_conditions:
                test_condition.setIsMet(False)

    #params can be anything. A Test container is expected to know what params to send its test conditions
    def testCondition(self, params):
        if self.testSubConditions(params):
            if self.selfTest(params):
                self.setIsMet(True)
                return True
            else:
                self.resetSubConditions()
        else:
            self.resetSubConditions()
        return False

    def printStatus(self):
        if not self.is_met:
            sub_not_met = False
            if self.test_conditions is not None:
                for test_condition in self.test_conditions:
                    if not test_condition.isMet():
                        sub_not_met = True
                        break
            print("Condition not met for: ", self.name)
            if self.test_conditions is not None and sub_not_met:
                print("Status of unmet sub conditions for: ", self.name)
                for test_condition in self.test_conditions:
                    test_condition.printStatus()

    #where the condition checks itself. Just returns True or False, does not set is_met
    def selfTest(self, params):
        pass



