import random
import sys
from time import time

DEBUG_PRINT = False
MIN_VAL = 0
MAX_VAL = 10

class Element:
    def __init__(self, value):
        self.value = value

class SortProfile:
    def __init__(self, statics = 0, dynamics = 0):
        self.static_elements = list()
        self.dynamic_elements = list()
        self.dynamic_map = dict()
        self.mixed_elements = list()
        self.statics_count = 0
        self.dynamics_count = 0
        #sort and process 2 seperate lists, statics and dynamics
        self.seperate_times = list()
        #sort and process statics/dynamics together in a list
        self.combined_times = list()

        if statics:
            self.addStatics(statics)
            self.sortStatics()
        if dynamics:
            self.addDynamics(dynamics)

    def addStaticElement(self):
        element = Element(random.randint(MIN_VAL,MAX_VAL))
        self.static_elements.append(element)
        self.mixed_elements.append(element)
        self.statics_count +=1

    #Keep a reference in the map for dynamic elements, so that they can be changed
    def addDynamicElement(self):
        element = Element(random.randint(MIN_VAL,MAX_VAL))
        self.dynamic_elements.append(element)
        self.mixed_elements.append(element)
        self.dynamic_map[self.dynamics_count] = element
        self.dynamics_count +=1

    def addStatics(self, count):
        numb = 0
        while numb < count:
            self.addStaticElement()
            numb+=1

    def addDynamics(self, count):
        numb = 0
        while numb < count:
            self.addDynamicElement()
            numb+=1

    def moveDynamics(self, percent = 100):
        if DEBUG_PRINT:
            print("Moving Dynamics")
        i = 0
        while i < self.dynamics_count:
            if random.randint(1,100) <= percent:
                self.dynamic_map[i].value = random.randint(MIN_VAL,MAX_VAL)
            i+=1

    def sortStatics(self):
        if DEBUG_PRINT:
            print("Sorting Statics")
        self.static_elements.sort(key=lambda x: x.value)

    def sortDynamics(self):
        if DEBUG_PRINT:
            print("Sorting Dynamics")
        self.dynamic_elements.sort(key=lambda x: x.value)

    def sortMixed(self):
        if DEBUG_PRINT:
            print("Sorting Mixed")
        self.mixed_elements.sort(key=lambda x: x.value)

    def printAll(self):
        print("\nStatic Elements: ")
        for element in self.static_elements:
            sys.stdout.write(str(element.value) + " ")
        print("\nDynamic Elements: ")
        for element in self.dynamic_elements:
            sys.stdout.write(str(element.value) + " ")
        print("\nDynamic Map: ")
        for element in self.dynamic_map.values():
            sys.stdout.write(str(element.value) + " ")
        print("\nMixed Elements: ")
        for element in self.mixed_elements:
            sys.stdout.write(str(element.value) + " ")
        print("\n")

    def processMixed(self):
        sum1 = 0
        for element in self.mixed_elements:
            sum1+=element.value
        return sum1

    def processStatics(self):
        sum1 = 0
        for element in self.static_elements:
            sum1+=element.value
        return sum1

    def processDynamics(self):
        sum1 = 0
        for element in self.dynamic_elements:
            sum1+=element.value
        return sum1

    def processStaticsAndDynamic(self):
        sum1 = 0
        static_index = 0
        dynamic_index = 0
        while static_index < self.statics_count and dynamic_index < self.dynamics_count:
            if self.static_elements[static_index].value < self.dynamic_elements[dynamic_index].value:
                sum1 += self.static_elements[static_index].value
                static_index +=1
            else:
                sum1 += self.dynamic_elements[dynamic_index].value
                dynamic_index += 1
        # there is atleast 1 static left and no dynamics
        if static_index < self.statics_count:
            while static_index < self.statics_count:
                sum1 += self.static_elements[static_index].value
                static_index += 1
        #there is atleast 1 dynamic left and no statics
        else:
            while dynamic_index < self.dynamics_count:
                sum1 += self.dynamic_elements[dynamic_index].value
                dynamic_index += 1

        return sum1

    def printTimes(self):
        print("Combined/Mixed list times:")
        print(self.combined_times)
        print("Seperate Times:")
        print(self.seperate_times)

    def printAverages(self):
        if len(self.combined_times) > 0:
            avg = sum(self.combined_times)/len(self.combined_times)
            print("Average time for Combined/Mixed list: " + str(avg))
        if len(self.seperate_times) > 0:
            avg = sum(self.seperate_times)/len(self.seperate_times)
            print("Average time for Seperate list: " + str(avg))

    def trial(self):
        self.moveDynamics()

        start = time()
        self.sortDynamics()
        self.processStaticsAndDynamic()
        end = time()
        self.seperate_times.append(end-start)

        start = time()
        self.sortMixed()
        self.processMixed()
        end = time()
        self.combined_times.append(end - start)

class SortProfileGrid:
    def __init__(self, profiles = 50, statics = 20, dynamics = 50):
        self.sort_profiles = list()
        prof_ct = 0
        while prof_ct < profiles:
            self.sort_profiles.append(SortProfile(statics, dynamics))
            prof_ct+=1
        #sort and process 2 seperate lists, statics and dynamics
        self.seperate_times = list()
        #sort and process statics/dynamics together in a list
        self.combined_times = list()

    def trial(self):
        for profile in self.sort_profiles:
            profile.moveDynamics()

        start = time()
        for profile in self.sort_profiles:
            profile.sortDynamics()
        for profile in self.sort_profiles:
            profile.processStaticsAndDynamic()
        end = time()
        self.seperate_times.append(end - start)

        start = time()
        for profile in self.sort_profiles:
            profile.sortMixed()
        for profile in self.sort_profiles:
            profile.processMixed()
        end = time()
        self.combined_times.append(end - start)

    def printAverages(self):
        if len(self.combined_times) > 0:
            avg = sum(self.combined_times)/len(self.combined_times)
            print("Average time for Combined/Mixed list: " + str(avg))
        if len(self.seperate_times) > 0:
            avg = sum(self.seperate_times)/len(self.seperate_times)
            print("Average time for Seperate list: " + str(avg))

MENU = """
Input choice:
-1: - Quit
0:  - Print
1:  - Move Dynamics
2:  - Sort
3:  - Process
4:  - Trial
5:  - Print Avg
"""

STATICS_CT = 100000
DYNAMICS_CT = 1000

if __name__ == "__main__":
    print("sort profile start")
    sp = SortProfile()
    spg = SortProfileGrid()
    #sp.addStatics(STATICS_CT)
    #sp.sortStatics()
    #sp.addDynamics(DYNAMICS_CT)
    keep_going = True
    while keep_going:
        try:
            choice = int(input(MENU))
            if choice == -1:
                keep_going = False
            elif choice == 0:
                sp.printAll()
            elif choice == 1:
                sp.moveDynamics()
            elif choice == 2:
                sp.sortStatics()
                sp.sortDynamics()
                sp.sortMixed()
            elif choice == 3:
                sum1 = sp.processDynamics()
                sum2 = sp.processStatics()
                sum3 = sp.processMixed()
                sum4 = sp.processStaticsAndDynamic()
                print(sum1, sum2, sum3, sum4)
            elif choice == 4:
                spg.trial()

            elif choice == 5:
                spg.printAverages()

        except Exception as e:
            print("Exception Caught")
            print(e)
    print("sort profile end")


























