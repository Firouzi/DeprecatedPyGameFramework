import json
import os
import shutil

from datetime import datetime

from Game_Scene.Test.Test_System.Rendering_test_parameters import GRID_SAVED_SCRIPTS_PATH, GRID_SCRIPT_PATH, \
    GRID_SUBSCRIPT_PATH, GRID_ARCHIVED_SCRIPTS_PATH, GRID_ARCHIVED_MAX

try:
    from send2trash import send2trash
    SEND_TO_TRASH = True
except Exception as e:
    SEND_TO_TRASH = False
    print("Exception caught during import send2trash")
    print(e)
    print('to install send2trash: ">>>pip install Send2Trash"')

#saves all executions in the debug loop to output scripts
#To prevent individual scripts from becoming too long, will chain them togeth
class ScriptSaver:
    MAX_SCRIPT_LENGTH = 1000
    SCRIPT_SAVE_INCREMENT = 500 #save the script every this number of commands

    def __init__(self, saved_scripts_path, save_script_folder = None, is_save_script = True):
        #if we do a reload game engine, we can start a new sequence instead of continuuing the chain
        self.script_sequence_number = 0
        self.saved_scripts_path = saved_scripts_path
        if save_script_folder is None:
            self.script_timestamp = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
            self.save_script_folder = self.script_timestamp + "_seq" + str(self.script_sequence_number) + "\\"
        else:
            self.save_script_folder = save_script_folder
        self.script_directory = self.saved_scripts_path + self.save_script_folder
        if not os.path.isdir(self.script_directory) and is_save_script:
            os.makedirs(self.script_directory)

        self.is_save = is_save_script
        self.current_script_number = 0
        self.current_length = 0
        self.script = list()

    def getScriptFolder(self):
        return self.save_script_folder

    def appendCommand(self, command, arguments):
        if not self.is_save:
            return
        self.script.append([command, arguments])
        self.current_length +=1
        if self.current_length >= ScriptSaver.MAX_SCRIPT_LENGTH:
            self.script.append([15,[self.current_script_number+1]]) #call to the next script
            self.saveScript()
            self.current_script_number += 1
            self.current_length = 0
            self.script = list()
        elif self.current_length % ScriptSaver.SCRIPT_SAVE_INCREMENT == 0:
            self.saveScript()

    def saveScript(self):
        if not self.is_save:
            return
        f = open(self.script_directory + str(self.current_script_number) + ".json", 'w')
        json.dump(self.script, f)
        f.close()

    #if there is a game engine reset, can start over with a new script sequence, since from this point on
    #repeating the same sequence will result in the same state
    #if remove_previous is true, then the past seqeunce is deleted
    def newScriptSequence(self):
        if not self.is_save:
            return
        #make sure current script is up to date
        self.saveScript()
        #setup the new sequence folder
        self.script_sequence_number +=1
        self.save_script_folder = self.script_timestamp + "_seq" + str(self.script_sequence_number)+ "\\"
        self.script_directory = self.saved_scripts_path + self.save_script_folder
        if not os.path.isdir(self.script_directory):
            os.makedirs(self.script_directory)
        self.current_script_number = 0
        self.current_length = 0
        self.script = list()

class ScriptLoader:
    def __init__(self,
                 script_directory = None,
                 saved_scripts_path = None,
                 archived_script_path = None,
                 subscript_directory = None,
                 script_cleanup = True):
        #If we pass in a directory, make sure not to delete it during cleanup
        if saved_scripts_path is None:
            self.saved_scripts_path = GRID_SAVED_SCRIPTS_PATH
        else:
            self.saved_scripts_path = saved_scripts_path
        if archived_script_path is None:
            self.archived_script_path = GRID_ARCHIVED_SCRIPTS_PATH
        else:
            self.archived_script_path = archived_script_path
        self._protected_directory = ""
        if script_directory is None:
            self.script_directory = GRID_SCRIPT_PATH
        else:
            self._protected_directory = script_directory
            self.script_directory = self.saved_scripts_path + script_directory + "\\"
        if subscript_directory is None:
            self.subscript_directory = GRID_SUBSCRIPT_PATH
        else:
            self.subscript_directory = subscript_directory

        if not os.path.isdir(self.archived_script_path):
            os.makedirs(self.archived_script_path)
        #Removes saved scripts which aren't tagged for storage
        try:
            if script_cleanup:
                self.scriptCleanup()
        except Exception as e:
            print("Exception caught during script cleanup")
            print(e)

    #For protecting the current script during cleanup
    def setProtectDirectory(self, protected_directory):
        self._protected_directory = protected_directory

    def setScriptPath(self, script_path = None):
        try:
            if script_path is None:
                script_path = input("enter script path:\n>>>")
            self.script_directory = self.saved_scripts_path + script_path + "\\"
        except Exception as e:
            print("Exception Caught in manualSetScriptPath")
            print(e)
            return ""
        return [script_path]

    #moves timestamped saved scripts which do not have an alpha character at start to trash
    def scriptCleanup(self):
        self.emptyArchive()
        folders = os.listdir(self.saved_scripts_path)
        for folder in folders:
            if os.path.isdir(self.saved_scripts_path + folder):
                if not folder == self._protected_directory and not folder[0].isalpha() and not folder[0] =="_":
                    #print("Archiving saved script: " + str(folder))
                    try:
                        shutil.copytree(self.saved_scripts_path+folder, self.archived_script_path+folder)
                        shutil.rmtree(self.saved_scripts_path+folder)
                    except Exception as e:
                        print("Exception caught moving folder to archive: " + str(folder))
                        print(e)

    #by archiving before deleting, we get a chance to save anything we didn't mean to delete
    def emptyArchive(self):
        folders = os.listdir(self.archived_script_path)
        if len(folders) > GRID_ARCHIVED_MAX:
            #print("Cleaning up script archive")
            for folder in folders:
                #print("Deleting " + str(folder))
                if SEND_TO_TRASH:
                    try:
                        send2trash(self.archived_script_path + folder)
                    except Exception as e:
                        print("Exception caught using send2trash")
                        print(e)
                else:
                    shutil.rmtree(self.archived_script_path + folder)

    def loadScript(self, script_id = None):
        if script_id is None:
            script_id = int(input("script_id: <#>\n>>>"))
        file = open(self.script_directory + str(script_id) + ".json")
        script = json.loads(file.read())
        file.close()
        return script, [script_id]

    def loadSubscript(self, subscript_id = None):
        if subscript_id is None:
            subscript_id = int(input("subscript_id: <#>\n>>>"))
        file = open(self.subscript_directory + str(subscript_id) + ".json")
        script = json.loads(file.read())
        file.close()
        return script, [subscript_id]

if __name__ == "__main__":
    script_loader = ScriptLoader()