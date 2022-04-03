'''
Created on Feb 26, 2017

@author: Robert
'''

from datetime import date, datetime
import os

'''
Class to log an error for debugging - logs to a timedate folder with file
    named by module and function which generated the error
@param module
@param function
@param description
'''
def logError(module, function, description):
    today = date.today()
    today = today.timetuple()
    folder = str(today[0])+str(today[1])+str(today[2])
    directory =  os.path.realpath('')+'\\dir_logging\\errors\\'+folder +'\\'
    if os.path.isdir(directory) == False:
        os.makedirs(directory)
    errorFile = open(directory+str(module)+'-'+str(function)+'.txt', 'a')
    errorFile.write(str(datetime.now())+' ' +description +'\n')
    errorFile.close()