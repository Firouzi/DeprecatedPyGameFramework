from threading import Lock, Thread
from input_handler import DEBUGGER_CONTROL_INPUT
#Can create a console window that will accept strings to be run as exec statements
#this is very powerful as it is run in GameEngine so has access to everything

#` : (lowercase ~ key) to start a debug console
#d : toggle on/off exec statements execute
    #statements wont be executed if toggled off.
#SPACEBAR : pause game (works active or not)
#+ : increase game speed by 0.1
#- : decrease game speed by 0.1
#a  : toggles camera manual control
#zscx : manually pan camera movement


class DebugHandler:


    change_game_speed = None
    pause_game = None

    def __init__(self):
        self.is_active = False
        self.is_console_running = False
        self.console_running_lock = Lock()
        self.exec_statements_queue = list() #[String] - a LIFO queue
        self.exec_statements_lock = Lock()
        DebuggerConsole.send_exec_statement = self.receiveExecStatement
        DebuggerConsole.send_death_rattle = self.debuggerConsoleDeath

        self.debounce_startconsole = False
        self.debounce_toggleactive = False
        self.debounce_pausegame = False

        self.key_state = dict()

    def update(self):
        pass

    def isActive(self):
        return self.is_active

    def hasNext(self):
        retVal = False
        self.exec_statements_lock.acquire()
        if len(self.exec_statements_queue) > 0:
            retVal = True
        self.exec_statements_lock.release()
        return retVal

    def next(self):
        retVal = ''
        self.exec_statements_lock.acquire()
        if len(self.exec_statements_queue) > 0:
            retVal = self.exec_statements_queue.pop(0)
        self.exec_statements_lock.release()
        return retVal

    def debuggerConsoleDeath(self):
        self.console_running_lock.acquire()
        self.is_console_running = False
        self.console_running_lock.release()

    def receiveExecStatement(self,
                              exec_statement):#String
        self.exec_statements_lock.acquire()
        self.exec_statements_queue.append(exec_statement)
        self.exec_statements_lock.release()

    #Unlike game entities we perform actions on the input as soon as it's received
    #We debounce by waiting for the key to be released
    def updateControlInputState(self,
                                entity_id,  #int - but don't care about it
                                key_state): #{CONTROL_INPUT : Bool}

        if key_state.get(DEBUGGER_CONTROL_INPUT.START_CONSOLE) and not self.debounce_startconsole:
            self.console_running_lock.acquire()
            if not self.is_console_running:
                self.is_console_running = True
                self.createDebuggerConsole()
            self.console_running_lock.release()
            self.debounce_startconsole = True

        if not key_state.get(DEBUGGER_CONTROL_INPUT.START_CONSOLE):
            self.debounce_startconsole = False

        if key_state.get(DEBUGGER_CONTROL_INPUT.TOGGLE_ACTIVE) and not self.debounce_toggleactive:
            if self.is_active:
                print('Debugging Toggled OFF')
            else:
                print('Debugging Toggled ON')
            self.is_active = not self.is_active
            self.debounce_toggleactive = True

        if not key_state.get(DEBUGGER_CONTROL_INPUT.START_CONSOLE):
            self.debounce_toggleactive = False

        if key_state.get(DEBUGGER_CONTROL_INPUT.PAUSE) and not self.debounce_pausegame:
            DebugHandler.pause_game()

        if not key_state.get(DEBUGGER_CONTROL_INPUT.PAUSE):
            self.debounce_pausegame = False

        if key_state.get(DEBUGGER_CONTROL_INPUT.SPEED_UP):
            DebugHandler.change_game_speed(0.1)

        if key_state.get(DEBUGGER_CONTROL_INPUT.SLOW_DOWN):
            DebugHandler.change_game_speed(-0.1)

    def createDebuggerConsole(self):
        debugger_console = DebuggerConsole()
        debugger_console.start()

class DebuggerConsole(Thread):
    send_exec_statement = None #func* GameEngine.debugAddExecStatement()
    send_death_rattle = None
    def __init__(self):
        Thread.__init__(self, daemon=True)

    def run(self):
        exec_statement = 'start'
        while exec_statement != '':
            exec_statement = str(input('Enter Exec Statement, or hit Enter to Quit\n>>>'))
            if exec_statement != '':
                DebuggerConsole.send_exec_statement(exec_statement)
                print('Exec Statement Sent')
        print("Quitting Debugger")
        DebuggerConsole.send_death_rattle()