'''
Created on Mar 5, 2017

@author: Robert
'''
import os, sys, unittest
sys.path.append(os.path.realpath('')+'\\dir_unitttest')

testmodules = [
    'test_actions',
    'test_actors',
    'test_events',
    'test_render',
    'test_scenery',
    'test_sound'
    ]

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))
  
unittest.TextTestRunner().run(suite)
