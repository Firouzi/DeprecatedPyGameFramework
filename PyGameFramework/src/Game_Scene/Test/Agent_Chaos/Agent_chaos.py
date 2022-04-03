#Agent Chaos is a system to 'Test the Tests'
#For every test, change the parameters of the game_engine such that the test should fail.
#If the test does not catch the issue, that is the same as a failure


import json
import os
import shutil
from datetime import datetime

try:
    from send2trash import send2trash
    SEND_TO_TRASH = True
except Exception as e:
    SEND_TO_TRASH = False
    print("Exception caught during import send2trash")
    print(e)
    print('to install send2trash: ">>>pip install Send2Trash"')

from Chaos_tests import CHAOS_TEST_GROUPS, CHAOS_TESTS

CHAOS_SCRIPT_DIRECTORY = "..\\Agent_Chaos\\Chaos_scripts\\"
CHAOS_ARCHIVE_DIRECTORY = "..\\Agent_Chaos\\Chaos_scripts\\_Archive\\"
CHAOS_ARCHIVE_MAX = 10

CHAOS_TRASH_MAX = 100

#TODO - add a way to archive and cleanup (delete) old chaos tests to keep from overloading the disk

class ChaosSaver:
    def __init__(self, is_active, script_directory = None, archive_directory = None):
        self.script_directory = script_directory
        if self.script_directory is None:
            self.script_directory = CHAOS_SCRIPT_DIRECTORY
        self.archive_directory = archive_directory
        if self.archive_directory is None:
            self.archive_directory = CHAOS_ARCHIVE_DIRECTORY

        self.current_script_folder = "" #To be created if active
        self.current_trash_directory = "" #To be created if active
        self.current_index = 0 #each new script dump goes into the script folder, numbered by this index
        #{"test name" : (args,)}
        self.current_script = dict()
        self.is_active = is_active
        #Move any current saved_script folders into the archive
        if is_active:
            self._archiveScripts()
            self.current_script_folder = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
            if not os.path.isdir(self.script_directory+self.current_script_folder):
                os.makedirs(self.script_directory+self.current_script_folder)
            #move trashed scripts here
            self.current_trash_directory = self.script_directory+self.current_script_folder + "\\_trash\\"
            if not os.path.isdir(self.current_trash_directory):
                os.makedirs(self.current_trash_directory)

    def trashCurrentScripts(self):
        self._emptyTrash()
        files = os.listdir(self.script_directory+self.current_script_folder+"\\")
        for file in files:
            try:
                shutil.copyfile(self.script_directory+self.current_script_folder+"\\" + file,
                                self.current_trash_directory + file)
                os.remove(self.script_directory+self.current_script_folder+"\\" + file)
            except Exception as e:
                print("Exception caught moving chaos file to trash: " + str(file))
                print(e)

    def _emptyTrash(self):
        files = os.listdir(self.current_trash_directory)
        if len(files) > CHAOS_TRASH_MAX:
            for file in files:
                if SEND_TO_TRASH:
                    try:
                        send2trash(self.current_trash_directory + file)
                    except Exception as e:
                        print("Exception caught using send2trash")
                        print(e)

    def getCurrentChaosId(self):
        return [self.current_script_folder, self.current_index]

    def addCommand(self, test_name, args):
        self.current_script[test_name] = args

    def saveScript(self):
        filename = self.script_directory+self.current_script_folder+"\\"+str(self.current_index) + ".json"
        f = open(filename, 'w')
        json.dump(self.current_script, f)
        f.close()
        self.newScript()

    #make sure to save first!
    def newScript(self):
        self.current_script = dict()
        self.current_index +=1

    def loadScript(self, chaos_id):
        try:
            filename = self.script_directory + chaos_id[0] + "\\" + str(chaos_id[1]) + ".json"
            file = open(filename)
        except:
            #if a "_" was prepended (to save from deleting), then check for that as well
            filename = self.script_directory + "_" + chaos_id[0] + "\\" + str(chaos_id[1]) + ".json"
            file = open(filename)
        script = json.loads(file.read())
        file.close()
        return script

    #To protect a script folder from archiving, prepend a '_' character on it
        #note that prepending '_' character to the folder will not change it's ID on a loadScript command
    def _archiveScripts(self):
        if not os.path.isdir(self.archive_directory):
            os.makedirs(self.archive_directory)
        self._emptyArchive()
        folders = os.listdir(self.script_directory)
        for folder in folders:
            if os.path.isdir(self.script_directory + folder):
                if not folder[0] =="_":
                    try:
                        shutil.copytree(self.script_directory+folder, self.archive_directory+folder)
                        shutil.rmtree(self.script_directory+folder)
                    except Exception as e:
                        print("Exception caught moving folder to archive: " + str(folder))
                        print(e)

    def _emptyArchive(self):
        folders = os.listdir(self.archive_directory)
        if len(folders) > CHAOS_ARCHIVE_MAX:
            #print("Cleaning up script archive")
            for folder in folders:
                #print("Deleting " + str(folder))
                if SEND_TO_TRASH:
                    try:
                        send2trash(self.archive_directory + folder)
                    except Exception as e:
                        print("Exception caught using send2trash")
                        print(e)
                else:
                    shutil.rmtree(self.archive_directory + folder)

#For every test (that has a chaos function), make a change to the game state that should
#be caught by the test. If the test does NOT catch this error, then we through a Chaos Error
#Uses Chaos saver to save the set of actions run, so that we can re-run the same chaos as needed
class AgentChaos:
    def __init__(self, is_save, is_silent = True):
        self.is_silent = is_silent
        self.chaos_saver = ChaosSaver(is_save)

    def trashCurrentScripts(self):
        self.chaos_saver.trashCurrentScripts()

    def runNewChaos(self, game_engine, test_collection):
        #this retval is the chaos_id used to rerun a script
        chaos_id = self.chaos_saver.getCurrentChaosId()
        for test_suite in test_collection:
            if test_suite[0]:
                for test in test_suite[1]:
                    if test[0]:
                        #If we are supposed to run this test, and chaos exists for it:
                        chaos_test_group = CHAOS_TEST_GROUPS.get(test[1].__name__)
                        if chaos_test_group is not None:
                            for chaos_test_name, chaos_test in chaos_test_group.items():
                                if not self.is_silent:
                                    print("Running Chaos test: ", chaos_test_name)
                                args, passing = chaos_test(game_engine)
                                self.chaos_saver.addCommand(chaos_test_name, args)
                                if not passing:
                                    print("Chaos test did not detect the error")
                                    self.chaos_saver.saveScript()
                                    return chaos_id, False

        self.chaos_saver.saveScript()
        return chaos_id, True

    def runSavedChaos(self, game_engine, chaos_id):
        chaos_script = self.chaos_saver.loadScript(chaos_id)
        for test_name, args in chaos_script.items():
            if not self.is_silent:
                print("Running Chaos test: ", test_name)
            args, passing = CHAOS_TESTS[test_name](game_engine, args)
            if not passing:
                return False
        return True

