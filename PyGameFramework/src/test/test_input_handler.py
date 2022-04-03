import unittest
from input_handler import InputHandler
import pygame

class KeyTest: #we just need a '.key' call to return an integer
    def __init__(self, key):
        self.key = key

class TestInputHandler(unittest.TestCase):
    #we track the keystates that get sent from all input handlers here
    def receive_input(self, entity_id, key_state):
        self.received_keystates.append(key_state)

    def buildInputHandler(self, active, blocking, consumer, successor):
        return InputHandler(component_id=0,
                            is_active=active,
                            is_blocking=blocking,
                            is_consumer=consumer,
                            input_map=self.input_map_none,
                            key_state=self.key_state_map,
                            send_input=self.receive_input,
                            successor=successor)

    def setUp(self): #called before each test
        self.key_state_map = {0:False, 1:False, 2:False, 3:False, 4:False,
                              6:False, 7:False, 8:False, 9:False, 10:False}
        self.input_map_all = {0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,10:10}
        self.input_map_none = dict()
        self.input_map_odd = {0:0,1:1,3:3,5:5,7:7,9:9}

        self.received_keystates = list()

    def reset_keystates(self):
        return {0:False, 1:False, 2:False, 3:False, 4:False, 6:False, 7:False, 8:False, 9:False, 10:False}

    def tearDown(self): #called after each test
        pass

    @classmethod
    def setUpClass(cls): #called once at beginning of test case
        pygame.init()

    @classmethod
    def tearDownClass(cls): #called once at end of test case
        pass

    def test_Blocking(self):
        keysdown = [KeyTest(0), KeyTest(1), KeyTest(2)]
        keysup = [KeyTest(7), KeyTest(8), KeyTest(9)]

        #final receiver (but should never get called due to blocking)
        input_handler_next = self.buildInputHandler(True, False, False, None)
        input_handler_next.input_map = self.input_map_all

        #Objects under test
        input_handler_ABC = self.buildInputHandler(True, True, True, input_handler_next)
        input_handler_BC = self.buildInputHandler(False, True, True, input_handler_next)
        input_handler_AB = self.buildInputHandler(True, True, False, input_handler_next)
        input_handler_B = self.buildInputHandler(False, True, False, input_handler_next)

        #initial receiver - not active passes so inputs through
        input_handler_previous = self.buildInputHandler(False, False, False, None)

        ###ACTIVE/BLOCKING/CONSUMER
        input_handler_previous.successor = input_handler_ABC
        # since we are blocking, even though no inputs are matched to not forward them
        self.received_keystates.clear()
        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 0)

        #some inputs are matched
        input_handler_ABC.input_map=self.input_map_all
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 1)
        self.assertEqual(self.received_keystates[0][1], True)
        self.assertEqual(self.received_keystates[0][8], False)

        ###BLOCKING/CONSUMER
        input_handler_previous.successor = input_handler_BC
        self.received_keystates.clear()
        self.assertEqual(len(self.received_keystates), 0)
        #no matches
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 0)

        input_handler_BC.input_map=self.input_map_all
        #matches but not active
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 0)

        #Testing the Non Actice non blocking non consumer as well
        input_handler_previous.input_map = self.input_map_all

        ###ACTIVE/BLOCKING
        input_handler_previous.successor = input_handler_AB
        # since we are blocking, even though no inputs are matched Do not forward them
        self.received_keystates.clear()
        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 0)

        #some inputs are matched
        input_handler_AB.input_map=self.input_map_all
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 1)
        self.assertEqual(self.received_keystates[0][2], True)
        self.assertEqual(self.received_keystates[0][4], False)

        ###BLOCKING
        input_handler_previous.successor = input_handler_B
        self.received_keystates.clear()
        self.assertEqual(len(self.received_keystates), 0)
        #no matches
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 0)

        input_handler_B.input_map=self.input_map_all
        #matches but not active
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 0)

    def test_Consumer(self):
        keysdown = [KeyTest(0), KeyTest(1), KeyTest(2)]
        keysup = [KeyTest(7), KeyTest(8), KeyTest(9)]

        #final receiver
        input_handler_next = self.buildInputHandler(True, False, False, None)
        input_handler_next.input_map = self.input_map_all

        #Objects under test (OUT)
        input_handler_AC = self.buildInputHandler(True, False, True, input_handler_next)
        input_handler_C = self.buildInputHandler(False, False, True, input_handler_next)
        input_handler_A = self.buildInputHandler(True, False, False, input_handler_next)

        #initial receiver - not active passes so inputs through
        input_handler_previous = self.buildInputHandler(False, False, False, None)

        ###ACTIVE/CONSUMER
        input_handler_previous.successor = input_handler_AC
        self.received_keystates.clear()
        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        #we did not have matches and passed on eveything
        #we dont call the send function if NO matches
        self.assertEqual(len(self.received_keystates), 1)
        #check final receiver keystates
        self.assertEqual(self.received_keystates[0][2], True) #true
        self.assertEqual(self.received_keystates[0][4], False)

        input_handler_AC.input_map = self.input_map_odd
        self.received_keystates.clear()
        input_handler_AC.key_state = self.reset_keystates()
        input_handler_next.key_state = self.reset_keystates()
        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        #consumed some inputs
        self.assertEqual(len(self.received_keystates), 2)
        #input_handler_AC
        self.assertEqual(self.received_keystates[0][0], True)
        self.assertEqual(self.received_keystates[0][1], True)
        self.assertEqual(self.received_keystates[0][2], False)
        self.assertEqual(self.received_keystates[0][7], False)
        #input_handler_next
        self.assertEqual(self.received_keystates[1][0], False) #Consumed!
        self.assertEqual(self.received_keystates[1][1], False) #Consumed!
        self.assertEqual(self.received_keystates[1][2], True) #Passed on
        self.assertEqual(self.received_keystates[1][7], False)

        ###CONSUMER
        input_handler_previous.successor = input_handler_C
        self.received_keystates.clear()
        input_handler_C.key_state = self.reset_keystates()
        input_handler_next.key_state = self.reset_keystates()

        input_handler_C.input_map = self.input_map_odd

        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        #not active, only final handler called send, no inputs consumed
        self.assertEqual(len(self.received_keystates), 1)
        self.assertEqual(self.received_keystates[0][0], True)
        self.assertEqual(self.received_keystates[0][1], True)
        self.assertEqual(self.received_keystates[0][2], True)
        self.assertEqual(self.received_keystates[0][7], False)

        ###ACTIVE
        input_handler_previous.successor = input_handler_A
        self.received_keystates.clear()
        input_handler_A.key_state = self.reset_keystates()
        input_handler_next.key_state = self.reset_keystates()

        self.assertEqual(len(self.received_keystates), 0)
        #empty map, all passed on with no send called
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 1)
        self.assertEqual(self.received_keystates[0][0], True)
        self.assertEqual(self.received_keystates[0][1], True)
        self.assertEqual(self.received_keystates[0][2], True)
        self.assertEqual(self.received_keystates[0][7], False)

        self.received_keystates.clear()
        input_handler_A.key_state = self.reset_keystates()
        input_handler_next.key_state = self.reset_keystates()
        input_handler_A.input_map = self.input_map_all
        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        #both get all of the inputs since not a consumer
        self.assertEqual(len(self.received_keystates), 2)
        self.assertEqual(self.received_keystates[0][0], True)
        self.assertEqual(self.received_keystates[0][1], True)
        self.assertEqual(self.received_keystates[0][2], True)
        self.assertEqual(self.received_keystates[0][7], False)
        self.assertEqual(self.received_keystates[1][0], True)
        self.assertEqual(self.received_keystates[1][1], True)
        self.assertEqual(self.received_keystates[1][2], True)
        self.assertEqual(self.received_keystates[1][7], False)

        ###3 Consumers Chained
        input_handler_previous.successor = input_handler_AC
        input_handler_AC2 = self.buildInputHandler(True, False, True, input_handler_next)
        input_handler_AC.successor = input_handler_AC2

        keysdown = [KeyTest(0), KeyTest(1), KeyTest(2), KeyTest(3), KeyTest(4), KeyTest(5)]
        self.received_keystates.clear()
        input_handler_AC.key_state = self.reset_keystates()
        input_handler_AC2.key_state = self.reset_keystates()
        input_handler_next.key_state = self.reset_keystates()

        input_handler_AC.input_map = {0:0, 1:1, 2:2}
        input_handler_AC2.input_map = {1:1, 2:2, 3:3, 4:4}

        self.assertEqual(len(self.received_keystates), 0)
        input_handler_previous.handleInput(keysdown, keysup, [])
        self.assertEqual(len(self.received_keystates), 3)
        #input_handler_AC
        self.assertEqual(self.received_keystates[0][0], True)
        self.assertEqual(self.received_keystates[0][1], True)
        self.assertEqual(self.received_keystates[0][2], True)
        self.assertEqual(self.received_keystates[0][3], False)
        #input_handler_AC2
        self.assertEqual(self.received_keystates[1][0], False) #consumed
        self.assertEqual(self.received_keystates[1][1], False) #consumed
        self.assertEqual(self.received_keystates[1][2], False) #consumed
        self.assertEqual(self.received_keystates[1][3], True)
        self.assertEqual(self.received_keystates[1][4], True)
        self.assertEqual(self.received_keystates[1][8], False)
        #input_handler_next
        self.assertEqual(self.received_keystates[2][0], False) #consumed
        self.assertEqual(self.received_keystates[2][1], False) #consumed
        self.assertEqual(self.received_keystates[2][2], False) #consumed
        self.assertEqual(self.received_keystates[2][3], False) #consumed
        self.assertEqual(self.received_keystates[2][4], False) #consumed
        self.assertEqual(self.received_keystates[2][5], True)
        self.assertEqual(self.received_keystates[2][9], False)