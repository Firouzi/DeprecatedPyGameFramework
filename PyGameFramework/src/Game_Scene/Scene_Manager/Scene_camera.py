from Game_Scene.Test.Mock_Classes.Grid_utility_mock import MockFlag
from enum import Enum

#indexes into the invisible border array
LEFT = 0
BOTTOM = 1
RIGHT = 2
TOP = 3

#This gets set when we evaluate the change cells, so that we know what transistion set to use
class CameraMovementEnum(Enum):
    NO_MOVEMENT = 0 #Initialized state as well
    UP = 1
    UP_OVERLAP = 2
    UP_RIGHT = 3
    UP_RIGHT_OVERLAP = 4
    RIGHT = 5
    RIGHT_OVERLAP = 6
    RIGHT_DOWN = 7
    RIGHT_DOWN_OVERLAP = 8
    DOWN = 9
    DOWN_OVERLAP = 10
    DOWN_LEFT = 11
    DOWN_LEFT_OVERLAP = 12
    LEFT = 13
    LEFT_OVERLAP = 14
    LEFT_UP = 15
    LEFT_UP_OVERLAP = 16
    INITIALIZED = 17
    SIZE_CHANGE = 18
    DETACH = 19 #When this is set, the next update will detach the camera from the scene

class CameraManager:
    def __init__(self):
        self._cameras = dict() #{camera_id : Camera}
        self._next_id = 1

    #Game enging does a get and then calls attach camera on the scene manager
    def getCamera(self, camera_id):
        return self._cameras[camera_id]

    #testing method
    def getCameraIds(self):
        return list(self._cameras.keys())

    def createCamera(self,
                     window_size,  # [x, y]px
                     activate_range,  # [x, y]px
                     deactivate_range):  # [x, y]px
        self._cameras[self._next_id] = SceneCamera(self._next_id, window_size, activate_range, deactivate_range)
        self._next_id +=1
        return self._next_id-1

    def removeCamera(self, camera_id):
        try:
            if self._cameras[camera_id].scene is not None:
                print("Tried to remove an attached camera, id: ",camera_id)
                assert False
            del(self._cameras[camera_id])
        except:
            pass

    def detachCamera(self, camera_id):
        try:
            self._cameras[camera_id].detachFromScene()
        except:
            pass

    def getCameraWindowSize(self, camera_id):
        return self._cameras[camera_id].getWindowSize()

    def setWindowSize(self, camera_id, window_size):
        self._cameras[camera_id].setWindowSize(window_size)

    def panCamera(self, camera_id, pan):
        self._cameras[camera_id].pan(pan)

    def moveCamera(self, camera_id, move):
        self._cameras[camera_id].move(move)

    #If a scene is removed, then any attached cameras should be detached immediately
    #This is a way for the game_engine to signal to CameraManager that a scene was removed
    def sceneRemovedFromCamera(self, scene_id):
        for camera in self._cameras.values():
            if camera.scene is not None and camera.scene.scene_id == scene_id:
                camera.detachFromScene()
                camera.scene = None

class SceneCamera:
    def __init__(self,
                 camera_id, #int
                 window_size, #[x, y]px
                 activate_range, #[x, y]px
                 deactivate_range): #[x, y]px
        self.camera_id = camera_id
        self.scene = None #reference to the Scene
        self._has_moved = MockFlag()
        self._position = [0, 0] #Top Left corner of scene
        #When the move flag is cleared, we store the position values as previous position
        self._previous_position = [0,0]

        self.world_size = None
        self.window_size = window_size
        self.activate_range = activate_range
        self.deactivate_range = deactivate_range

        #This is set by the MasterGrid during the change state method to determine transition sequence
        self.camera_movement_enum = CameraMovementEnum.NO_MOVEMENT
        self.current_active_col_range = [0,0]
        self.current_active_row_range = [0,0]
        self.previous_active_row_range = [0,0]
        self.previous_active_col_range = [0,0]
        #The invisible border is inclusive.  Any rows/columns that are in the active range outside of the invisible
        #borders are invisible cells (these cells are still updated)
        self.borders_labels_temp = ("LEFT", "BOTTOM", "RIGHT", "TOP")
        self.current_invisible_border = [0, 0, 0, 0] #[left, bottom, right, top]
        self.previous_invisible_border = [0, 0, 0, 0]

        #These are only checked and updated in the testing method
        self.__previous_camera_position__ = None
        #Set them to None, so that the first time running the test we initialize them
        self.__previous_active_row_range__ = None
        self.__previous_active_col_range__ = None
        #For testing - when there is a size change, we don't follow all of the histeresis 'rules'.
        #There will be a different test case to cover it
        #So we will set this var when size changes, and then during test, clear it
        self.__has_changed_size__ = False
    #returns True is the row/column is within the range of current active row/col
    def isInActiveRange(self, row, col):
        return (self.current_active_row_range[0] <= row <= self.current_active_row_range[1]) and \
               (self.current_active_col_range[0] <= col <= self.current_active_col_range[1])

    def isInVisibleRange(self, row, col):
        return (self.current_invisible_border[TOP] <= row <= self.current_invisible_border[BOTTOM]) and \
               (self.current_invisible_border[LEFT] <= col <= self.current_invisible_border[RIGHT])

    #Set initial called in the initialize method in MasterGrid
    def setInitialPosition(self, position):
        self._position = list(position)
        self._previous_position = list(position)
        self.__previous_camera_position__ = None #For tests
        self._has_moved.value = True

    def setInitialInvisibleBorders(self, left, bottom, right, top):
        self.current_invisible_border = [left, bottom, right, top]
        self.previous_invisible_border = [left, bottom, right, top]

    def setInitialActiveRowRange(self, row_range):
        self.current_active_row_range = list(row_range)
        self.previous_active_row_range = list(row_range)
        self.__previous_active_row_range__ = None #For tests

    def setInitialActiveColRange(self, col_range):
        self.current_active_col_range = list(col_range)
        self.previous_active_col_range = list(col_range)
        self.__previous_active_col_range__ = None #For tests

    def setInvisibleBorders(self, left, bottom, right, top):
        self.current_invisible_border = [left, bottom, right, top]

    def setActiveRowRange(self, row_range):
        self.current_active_row_range = row_range

    def setActiveColRange(self, col_range):
        self.current_active_col_range = col_range

    def setMovementEnum(self, camera_movement_enum):
        self.camera_movement_enum = camera_movement_enum

    def hasMoved(self):
        return self._has_moved.value

    def getPosition(self):
        return list(self._position)

    def getPreviousPosition(self):
        return list(self._previous_position)

    def getInvisibleBorder(self):
        return self.current_invisible_border

    def getActiveColumnRange(self):
        return self.current_active_col_range

    def getActiveRowRange(self):
        return self.current_active_row_range

    def getPreviousInvisibleBorder(self):
        return self.previous_invisible_border

    def getPreviousColRange(self):
        return self.previous_active_col_range

    def getPreviousRowRange(self):
        return self.previous_active_row_range

    def getCameraMovementEnum(self):
        return self.camera_movement_enum

    def getWindowSize(self):
        return self.window_size

    def getActivateRange(self):
        return self.activate_range

    def getDeactivateRange(self):
        return self.deactivate_range

    #Clear the move flag, and store the current position value as previous
    #If the flag is set, can look at the diff of prev/current to see the change
    def clearHasMoved(self):
        self._has_moved.value = False
        self.camera_movement_enum = CameraMovementEnum.NO_MOVEMENT
        self.previous_active_row_range = list(self.current_active_row_range)
        self.previous_active_col_range = list(self.current_active_col_range)
        self._previous_position = list(self._position)
        self.previous_invisible_border = list(self.current_invisible_border)

    def attachToScene(self, scene, position):
        if self.scene is not None:
            print("Tried to attach attached camera",str(self.camera_id),str(scene))
            assert False
        #Re initialze all the values to be updated by the new grid
        self.camera_movement_enum = CameraMovementEnum.NO_MOVEMENT
        self.current_active_col_range = [0,0]
        self.current_active_row_range = [0,0]
        self.previous_active_row_range = [0,0]
        self.previous_active_col_range = [0,0]
        self.current_invisible_border = [0, 0, 0, 0]
        self.previous_invisible_border = [0, 0, 0, 0]
        self.scene = scene
        self.world_size = scene.getWorldSize()
        self.setInitialPosition(position)
        self.checkBoundary()
        #Flag being set so that on next update cell states get changed
        self._has_moved.value = True

    def detachFromScene(self):
        if self.scene is None:
            print("Tried to detach dettached camera",str(self.camera_id))
            assert False
        #On the next update, the camera will be removed from the grid
        #You cannot re-attach the camera until the next update
        #Any movement since the previous update will be disregarded
        self._has_moved.value = True
        self.camera_movement_enum = CameraMovementEnum.DETACH
        self.current_invisible_border = [-1,-1,-1,-1]
        self.current_active_col_range = [-1,-1]
        self.current_active_row_range = [-1,-1]

    def setWindowSize(self, window_size):
        #No going back on a detach!
        if self.camera_movement_enum != CameraMovementEnum.DETACH and \
                self.camera_movement_enum != CameraMovementEnum.INITIALIZED:
            self.window_size = window_size
            self.camera_movement_enum = CameraMovementEnum.SIZE_CHANGE
            self._has_moved.value = True
            self.__has_changed_size__ = True #This is only needed for testing
            return True
        return False

    def pan(self, pan): #[int, int]
        if self.scene is not None:# and self.scene.is_active:
            self._position[0] += pan[0]
            self._position[1] += pan[1]
            self.checkBoundary()
            self._has_moved.value = True
            return True
        return False

    def move(self, position): #[int, int]
        if self.scene is not None:# and self.scene.is_active:
            #don't destroy refs, set each index don't reset the object
            self._position[0] = position[0]
            self._position[1] = position[1]
            self.checkBoundary()
            self._has_moved.value = True
            return True
        return False

    def checkBoundary(self):
        if self._position[0] > self.world_size[0] - self.window_size[0]:
            self._position[0] = self.world_size[0] - self.window_size[0]
        if self._position[0] < 0:
            self._position[0] = 0
        if self._position[1] > self.world_size[1] - self.window_size[1]:
            self._position[1] = self.world_size[1] - self.window_size[1]
        if self._position[1] < 0:
            self._position[1] = 0