from Game_Scene.Scene_Cell.Scene_master_cell import MasterCell
from Game_Scene.Scene_Manager.Scene_camera import CameraMovementEnum
from Game_Scene.Scene_Cell.Scene_cell import CellStateEnum

#indexes into the invisible border array
LEFT = 0
BOTTOM = 1
RIGHT = 2
TOP = 3


#The state of the cells based on the camera(s) is the same across all layers
#The master grid determines cell state, then sets the state for the cells in each layer
class SceneMasterGrid:
    def __init__(self, scene):
        self.scene = scene

        self._cameras = dict() #{camera_id : Camera}
        #The master grid uses the cameras to determine the active cell ranges
        self._scene_grids = dict() #{layer_id : SceneGrid}

        # function pointers to notify the entity_manager when sprites go into and out of active cells
        self.notify_sprite_offscreen = None  # EntityManager.notifySpriteOffScreen(entity_id)
        self.notify_sprite_onscreen = None  # EntityManager.notifySpriteOnScreen(entity_id)

        self.cell_size = scene.getCellSize()
        self.world_size = scene.getWorldSize()
        self.tile_size = scene.getTileSize()

        self.master_cells = list()
        self.numb_rows = 0 #updated in createGrid()
        self.numb_cols = 0

        #Used to arrange the cameras into a list of rows, so that the cell updates are done in order
        #call self.generateUpdateRows() to update them before updating the cells
        self.update_cell_ranges = dict()  # {row : [[col_min1, colmax1], [col_min2, col_max2],...]}
        self.row_update_keys = list()  # list of row ints in ascending order

        self.createGrid()

    def activateGrid(self):
        #If the camera was detached during scene's inactive period, just remove it now
        detach_cameras = list()
        for camera_id, camera in self._cameras.items():
            if camera.camera_movement_enum == CameraMovementEnum.DETACH:
                detach_cameras.append(camera_id)
            else:
                self._initializeCamera(camera)
        for camera_id in detach_cameras:
            self._detachCamera(camera_id)

    #Transitions all currently active cells to inactive
    def deactivateGrid(self):
        for camera in self._cameras.values():
            for row in range(camera.previous_active_row_range[0], camera.previous_active_row_range[1] + 1):
                for col in range(camera.previous_active_col_range[0], camera.previous_active_col_range[1] + 1):
                        self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
        for camera in self._cameras.values():
            self.transitionCells((camera.previous_active_row_range[0], camera.previous_active_row_range[1] + 1),
                                 (camera.previous_active_col_range[0], camera.previous_active_col_range[1] + 1))

    def attachCamera(self, camera_id, camera):
        self._cameras[camera_id] = camera
        if self.scene.is_active:
            self._initializeCamera(camera)

    def _detachCamera(self, camera_id):
        try:
            self._cameras[camera_id].scene = None
            self.scene.detachCamera(camera_id)
            del (self._cameras[camera_id])
        except:
            pass

    def addSceneGrid(self, layer_id, scene_grid):
        #The newly created grid will carry the current cell states
        #there are no transition needed because new grids do not have any entities yet
        self._scene_grids[layer_id] = scene_grid

    def removeSceneGrid(self, layer_id):
        try:
            del(self._scene_grids[layer_id])
        except:
            pass

    def createGrid(self):
        #The modulos boolean operation adds 1 if we don't have the cell border align with the world border
        self.numb_rows = self.world_size[1] // self.cell_size[1] + (self.world_size[1] % self.cell_size[1] != 0)
        self.numb_cols = self.world_size[0] // self.cell_size[0] + (self.world_size[0] % self.cell_size[0] != 0)

        cell_id = 0
        top_px = 0
        bottom_px = self.cell_size[1] - 1
        row_ct = 0
        while row_ct < self.numb_rows:
            left_px = 0
            right_px = self.cell_size[0] - 1
            cell_row = list()
            col_ct = 0
            while col_ct < self.numb_cols:
                borders = (left_px, bottom_px, right_px, top_px)
                cell_row.append(MasterCell(self, cell_id, borders, row_ct, col_ct, CellStateEnum.CELL_STATE_INACTIVE))
                cell_id+=1
                left_px = right_px +1
                right_px = right_px + self.cell_size[0]
                if right_px >= self.world_size[0]:
                    right_px = self.world_size[0] - 1
                col_ct+=1
            self.master_cells.append(cell_row)
            top_px = bottom_px + 1
            bottom_px = bottom_px + self.cell_size[1]
            if bottom_px >= self.world_size[1]:
                bottom_px = self.world_size[1] - 1
            row_ct+=1

    #When the camera is attached, it will have initial values of [0,0] for active row and col
    #By setting them here, we will be certain to have the cells states changed and transitioned on the next update
    def _initializeCamera(self, camera):
        camera_position = camera.getPosition()
        camera.setInitialPosition(camera_position)
        window_size = camera.getWindowSize()
        activate_range = camera.getActivateRange()
        #columns less than this value are completely off camera
        left_border = (camera_position[0])// self.cell_size[0]
        # columns greater than this value are completely off camera
        right_border = (camera_position[0] + window_size[0] - 1)// self.cell_size[0]
        if right_border >= self.numb_cols:
            right_border = self.numb_cols - 1
        #rows less than this value are completely off camera
        top_border = (camera_position[1])// self.cell_size[1]
        # rows greater than this value are completely off camera
        bottom_border = (camera_position[1] + window_size[1] - 1)// self.cell_size[1]
        if bottom_border >= self.numb_rows:
            bottom_border = self.numb_rows -1
        camera.setInitialInvisibleBorders(left_border, bottom_border, right_border, top_border)
        row_start = (camera_position[1] - activate_range[1]) // self.cell_size[1]
        if row_start < 0:
            row_start = 0
        row_end = (camera_position[1] + window_size[1] - 1 + activate_range[1]) // self.cell_size[1]
        if row_end >= self.numb_rows:
            row_end = self.numb_rows -1
        col_start = (camera_position[0] - activate_range[0]) // self.cell_size[0]
        if col_start < 0:
            col_start = 0
        col_end = (camera_position[0] + window_size[0] - 1 + activate_range[0]) // self.cell_size[0]
        if col_end >= self.numb_cols:
            col_end = self.numb_cols - 1
        camera.setInitialActiveRowRange([row_start, row_end])
        camera.setInitialActiveColRange([col_start, col_end])
        camera.setMovementEnum(CameraMovementEnum.INITIALIZED)
        #Cells will be state changed and transitioned on the next update()

    #Check all excluded camera_ids to see if any have the passed in row/col within their active range
    def checkCamerasForActive(self, exclude_camera_id, row, col):
        for camera_id, camera in self._cameras.items():
            if camera_id != exclude_camera_id:
                if camera.isInActiveRange(row, col):
                    return True
        return False

    #Check all excluded camera_ids to see if any have the passed in row/col within their visible range
    def checkCamerasForVisible(self, exclude_camera_id, row, col):
        for camera_id, camera in self._cameras.items():
            if camera_id != exclude_camera_id:
                if camera.isInVisibleRange(row, col):
                    return True
        return False

    #Takes all current cameras update ranges.  Makes a list of rows, ordered from least to greatest.
    #Each Row has the column range to update.
    #Where rows and columns overlap between 2 cameras, make the range a superset of each
    #Where the rows are the same, but the columns do not overlap, create 2 entries ordered by starting col
    #This allows updating all active cells in order from low to high ID, and not updating any cells twice.
    #Returns an ordered int list of unique row keys, and a dict
    #The dict is keyed on the row, and returns a list of column ranges to update
    #{row : [[col_min1, colmax1], [col_min2, col_max2],...]}
    #To use, key on the dict using the ordered int list, and iterate over each col range returned.
    def generateUpdateRows(self):
        # takes the existing column ranges, and either appends, or modifies them to incorporate new col range
        def conflateRow(current_col_ranges, new_col_range):
            # handle the case that the new range goes in front
            if new_col_range[1] <= current_col_ranges[0][1]:
                # not overlapped, insert it in front
                if new_col_range[1] < current_col_ranges[0][0]:
                    current_col_ranges.insert(0, new_col_range)
                # overlapped, just extend it
                elif new_col_range[0] < current_col_ranges[0][0]:
                    current_col_ranges[0][0] = new_col_range[0]
                return
            # handle the case that the new range goes in back
            if new_col_range[0] >= current_col_ranges[-1][0]:
                # not overlapping, append it
                if new_col_range[0] > current_col_ranges[-1][1]:
                    current_col_ranges.append(new_col_range)
                # overlapped, just extend it
                elif new_col_range[1] > current_col_ranges[-1][1]:
                    current_col_ranges[-1][1] = new_col_range[1]
                return
            # the new range fits somewhere in the middle of the existing ranges
            for i in range(0, len(current_col_ranges)):
                # we look for the index that the new col range should be inserted
                if new_col_range[0] < current_col_ranges[i][1]:
                    # if the entire range is less than the current index, insert it
                    if new_col_range[1] < current_col_ranges[i][0]:
                        # if overlapping previous range, extend that range
                        if i > 0 and new_col_range[0] <= current_col_ranges[i - 1][1]:
                            current_col_ranges[i - 1][1] = new_col_range[1]
                        # no overlap on either side, insert it
                        else:
                            current_col_ranges.insert(i, new_col_range)
                        return
                    # if the new col range does not exceed the current index
                    if new_col_range[1] <= current_col_ranges[i][1]:
                        # if new range is larger, extend it
                        if new_col_range[0] < current_col_ranges[i][0]:
                            current_col_ranges[i][0] = new_col_range[0]
                            # We don't need to overlap the previous range
                            if i > 0 and current_col_ranges[i][0] <= current_col_ranges[i - 1][1]:
                                current_col_ranges[i][0] = current_col_ranges[i - 1][1] + 1
                        return
                    # now we know the end of the new range exceeds the end of the current index
                    # if the new range completly consumes the current index
                    if new_col_range[0] < current_col_ranges[i][0]:
                        current_col_ranges[i] = new_col_range
                        # We don't need to overlap the previous range
                        if i > 0 and current_col_ranges[i][0] <= current_col_ranges[i - 1][1]:
                            current_col_ranges[i][0] = current_col_ranges[i - 1][1] + 1
                    else:
                        # we extend the current range so that it included both
                        current_col_ranges[i][1] = new_col_range[1]
                    # now we need to make sure we have not overlapped any of the following ranges
                    range_end = current_col_ranges[i][1]  # keep going until we have covered to this point
                    for j in range(i + 1, len(current_col_ranges)):
                        # if the new range exceeds the start of the current index
                        if range_end >= current_col_ranges[j][0]:
                            # set the end of the previous range to border the start of the new range
                            current_col_ranges[j - 1][1] = current_col_ranges[j][0] - 1
                        else:
                            # extend the previous index to range end if it is less
                            if range_end > current_col_ranges[j - 1][1]:
                                current_col_ranges[j - 1][1] = range_end
                            return
                    if current_col_ranges[-1][1] < range_end:
                        current_col_ranges[-1][1] = range_end
                    return

        self.update_cell_ranges = dict()  # {row : [[col_min1, colmax1], [col_min2, col_max2],...]}
        self.row_update_keys = list()  # list of row ints in ascending order
        for camera in self._cameras.values():
            col_range = camera.current_active_col_range
            for row in range(camera.current_active_row_range[0], camera.current_active_row_range[1] + 1):
                # If we already have this row, either extend an existing col range, or append it
                if self.update_cell_ranges.get(row) is not None:
                    conflateRow(self.update_cell_ranges.get(row), list(col_range))
                else:
                    self.update_cell_ranges[row] = [list(col_range)]
                    self.row_update_keys.append(row)
        self.row_update_keys.sort()

    #On an update, if a camera has changed size, than just treat it as initialized
    def _updateCameraSizeChange(self, camera):
        camera_position = camera.getPosition()
        window_size = camera.getWindowSize()
        activate_range = camera.getActivateRange()
        # columns less than this value are completely off camera
        left_border = (camera_position[0]) // self.cell_size[0]
        # columns greater than this value are completely off camera
        right_border = (camera_position[0] + window_size[0] - 1) // self.cell_size[0]
        if right_border >= self.numb_cols:
            right_border = self.numb_cols - 1
        # rows less than this value are completely off camera
        top_border = (camera_position[1]) // self.cell_size[1]
        # rows greater than this value are completely off camera
        bottom_border = (camera_position[1] + window_size[1] - 1) // self.cell_size[1]
        if bottom_border >= self.numb_rows:
            bottom_border = self.numb_rows - 1
        camera.setInitialInvisibleBorders(left_border, bottom_border, right_border, top_border)
        row_start = (camera_position[1] - activate_range[1]) // self.cell_size[1]
        if row_start < 0:
            row_start = 0
        row_end = (camera_position[1] + window_size[1] - 1 + activate_range[1]) // self.cell_size[1]
        if row_end >= self.numb_rows:
            row_end = self.numb_rows - 1
        col_start = (camera_position[0] - activate_range[0]) // self.cell_size[0]
        if col_start < 0:
            col_start = 0
        col_end = (camera_position[0] + window_size[0] - 1 + activate_range[0]) // self.cell_size[0]
        if col_end >= self.numb_cols:
            col_end = self.numb_cols - 1
        camera.setActiveRowRange([row_start, row_end])
        camera.setActiveColRange([col_start, col_end])

    #This is the MULTI camera logic for updating the active cell ranges.
    #In the direction a camera is moving, we use the activate range (cells are activated before on screen)
    #In the opposite direction, use the deactivate range to determine cells to deactivate.
    #This creates a hysteresis so that cells don't alternate active/inactive rapidly if the camera jitters back and forth
    #Additonal Rules This Algorithm Creates:
        #Cannot deactivate a cell in the direction that camera moves, meaning moving right no cells to right will deactivate
        #Active Cells form a rectangle, all rows/cols are the same length/width.
        #The consequence of the above rules, depending on camera movement sequence, can see cells activating further than activate range
        #This is OK!
    #Any active cells that have no part onscreen are invisible (still actively updated).
    #This invisible border is determined.  The border visible, outside of border is invisible.
        #EG, if the TOP border is row 2, row 2 is VISIBLE, any ACTIVE rows less than row 2 (row 1 etc) are INVISIBLE
    #Method has 3 parts.  Each past is done on all cameras before the next part:
        #Part 1: set active range
        #Part 2: set cell state
        #Part 3: call cell transitions
    def _updateActiveCells(self):
        remove_camera_ids = list()
        #PART 1: Update the active and invisible range of all cameras
        for camera_id, camera in self._cameras.items():
            if camera.camera_movement_enum == CameraMovementEnum.SIZE_CHANGE:
                self._updateCameraSizeChange(camera)
                continue #we are done with this phase for a moved camera
            if not camera.hasMoved() or camera.camera_movement_enum == CameraMovementEnum.DETACH:
                continue
            camera_position = camera.getPosition()
            window_size = camera.getWindowSize()
            activate_range = camera.getActivateRange()
            deactivate_range = camera.getDeactivateRange()
            #Note: the prev vals are updated by camera when the move flag is cleared,
                #thus at this point prev and cur values are actually the same
            prev_invisible_border = list(camera.getPreviousInvisibleBorder())
            previous_camera_position = camera.getPreviousPosition()
            prev_col_range = camera.getPreviousColRange()
            prev_row_range = camera.getPreviousRowRange()
            #Update the invisible border
            # columns less than this value are completely off camera
            left_border = (camera_position[0]) // self.cell_size[0]
            # columns greater than this value are completely off camera
            right_border = (camera_position[0] + camera.window_size[0] - 1) // self.cell_size[0]
            if right_border >= self.numb_cols:
                right_border = self.numb_cols - 1
            # rows less than this value are completely off camera
            top_border = (camera_position[1]) // self.cell_size[1]
            # rows greater than this value are completely off camera
            bottom_border = (camera_position[1] + camera.window_size[1] - 1) // self.cell_size[1]
            if bottom_border >= self.numb_rows:
                bottom_border = self.numb_rows - 1
            camera.setInvisibleBorders(left_border, bottom_border, right_border, top_border)
            current_invisible_border = camera.getInvisibleBorder()
            #If there is no change in the cell states for this camera, we will not need to transition anything (will 'continue' loop)
            invisible_has_changed = (current_invisible_border[RIGHT] != prev_invisible_border[RIGHT]) or \
                                    (current_invisible_border[LEFT] != prev_invisible_border[LEFT]) or \
                                    (current_invisible_border[TOP] != prev_invisible_border[TOP]) or \
                                    (current_invisible_border[BOTTOM] != prev_invisible_border[BOTTOM])
            # moved right
            if camera_position[0] > previous_camera_position[0]:
                # left most column that should remain active accounting for deactivation hysteresis
                # This column may not be active, if the activation range was never reached, but if active should remain active
                minimum_active_col = (camera_position[0] - deactivate_range[0]) // self.cell_size[0]
                # do not increase the minimum value when moving right
                if minimum_active_col < prev_col_range[0]:
                    minimum_active_col = prev_col_range[0]
                elif minimum_active_col < 0:
                    minimum_active_col = 0
                maximum_active_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // \
                                     self.cell_size[0]
                # we could see this condition if having moved left we have a further right cell activated due to deact hist
                if maximum_active_col < prev_col_range[1]:
                    maximum_active_col = prev_col_range[1]
                elif maximum_active_col >= self.numb_cols:
                    maximum_active_col = self.numb_cols - 1
                active_col_has_changed = (minimum_active_col != prev_col_range[0]) or \
                                         (maximum_active_col != prev_col_range[1])
                # moved right-down
                if camera_position[1] > previous_camera_position[1]:
                    minimum_active_row = (camera_position[1] - deactivate_range[1]) // self.cell_size[1]
                    if minimum_active_row < prev_row_range[0]:
                        minimum_active_row = prev_row_range[0]
                    elif minimum_active_row < 0:
                        minimum_active_row = 0
                    maximum_active_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // self.cell_size[1]
                    if maximum_active_row < prev_row_range[1]:
                        maximum_active_row = prev_row_range[1]
                    elif maximum_active_row >= self.numb_rows:
                        maximum_active_row = self.numb_rows - 1
                    active_row_has_changed = (minimum_active_row != prev_row_range[0]) or \
                                             (maximum_active_row != prev_row_range[1])
                    if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                                not (active_row_has_changed or active_col_has_changed or invisible_has_changed):
                        camera.clearHasMoved()
                        continue
                    # right-down, no overlap
                    if minimum_active_col > prev_col_range[1] or minimum_active_row > prev_row_range[1]:
                        # switch to using the activate histeresis (all current is going to be deactivated)
                        minimum_active_col = (camera_position[0] - activate_range[0]) // self.cell_size[0]
                        if minimum_active_col < 0:
                            minimum_active_col = 0
                        minimum_active_row = (camera_position[1] - activate_range[1]) // self.cell_size[1]
                        if minimum_active_row < 0:
                            minimum_active_row = 0
                        camera.setMovementEnum(CameraMovementEnum.RIGHT_DOWN)
                    # right-down, screen overlaps
                    else:
                        camera.setMovementEnum(CameraMovementEnum.RIGHT_DOWN_OVERLAP)
                    camera.setActiveRowRange([minimum_active_row, maximum_active_row])
                # moved right-up
                elif camera_position[1] < previous_camera_position[1]:
                    maximum_active_row = (camera_position[1] + window_size[1] + deactivate_range[1] - 1) // \
                                         self.cell_size[1]
                    if maximum_active_row > prev_row_range[1]:
                        maximum_active_row = prev_row_range[1]
                    elif maximum_active_row >= self.numb_rows:
                        maximum_active_row = self.numb_rows - 1
                    minimum_active_row = (camera_position[1] - activate_range[1]) // self.cell_size[1]
                    if minimum_active_row > prev_row_range[0]:
                        minimum_active_row = prev_row_range[0]
                    elif minimum_active_row < 0:
                        minimum_active_row = 0
                    active_row_has_changed = (minimum_active_row != prev_row_range[0]) or \
                                             (maximum_active_row != prev_row_range[1])
                    if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                            not (active_row_has_changed or active_col_has_changed or invisible_has_changed):
                        camera.clearHasMoved()
                        continue
                    #right-up, no overlap
                    if minimum_active_col > prev_col_range[1] or maximum_active_row < prev_row_range[0]:
                        # switch to using the activate histeresis (all current is going to be deactivated)
                        minimum_active_col = (camera_position[0] - activate_range[0]) // self.cell_size[0]
                        if minimum_active_col < 0:
                            minimum_active_col = 0
                        maximum_active_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // \
                                             self.cell_size[1]
                        if maximum_active_row >= self.numb_rows:
                            maximum_active_row = self.numb_rows - 1
                        camera.setMovementEnum(CameraMovementEnum.UP_RIGHT)
                    # right-up, screen overlaps
                    else:
                        camera.setMovementEnum(CameraMovementEnum.UP_RIGHT_OVERLAP)
                    camera.setActiveRowRange([minimum_active_row, maximum_active_row])
                # only moved right
                else:
                    if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                            not (active_col_has_changed or invisible_has_changed):
                        camera.clearHasMoved()
                        continue
                    # only right no overlap
                    if minimum_active_col > prev_col_range[1]:
                        # switch to using the activate histeresis (all current is going to be deactivated)
                        minimum_active_col = (camera_position[0] - activate_range[0]) // self.cell_size[0]
                        if minimum_active_col < 0:
                            minimum_active_col = 0
                        camera.setMovementEnum(CameraMovementEnum.RIGHT)
                    # only right screen overlaps
                    else:
                        camera.setMovementEnum(CameraMovementEnum.RIGHT_OVERLAP)
                # update current active cell range (after any of the move-right branches)
                camera.setActiveColRange([minimum_active_col, maximum_active_col])
            # moved left
            elif camera_position[0] < previous_camera_position[0]:
                # right most column that should remain active accounting for deactivation hysteresis
                # This column may not be active, if the activation range was never reached, but if active should remain active
                maximum_active_col = (camera_position[0] + window_size[0] + deactivate_range[0] - 1) // \
                                     self.cell_size[0]
                # do not increase the maximum value when moving left
                if maximum_active_col > prev_col_range[1]:
                    maximum_active_col = prev_col_range[1]
                elif maximum_active_col >= self.numb_cols:
                    maximum_active_col = self.numb_cols - 1
                minimum_active_col = (camera_position[0] - activate_range[0]) // self.cell_size[0]
                # there could be a lower curent col number due to the deactivation histeresis, in which case we keep it active
                if minimum_active_col > prev_col_range[0]:
                    minimum_active_col = prev_col_range[0]
                elif minimum_active_col < 0:
                    minimum_active_col = 0
                active_col_has_changed = (minimum_active_col != prev_col_range[0]) or \
                                         (maximum_active_col != prev_col_range[1])
                # moved left-down
                if camera_position[1] > previous_camera_position[1]:
                    minimum_active_row = (camera_position[1] - deactivate_range[1]) // self.cell_size[1]
                    if minimum_active_row < prev_row_range[0]:
                        minimum_active_row = prev_row_range[0]
                    elif minimum_active_row < 0:
                        minimum_active_row = 0
                    maximum_active_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // \
                                         self.cell_size[1]
                    if maximum_active_row < prev_row_range[1]:
                        maximum_active_row = prev_row_range[1]
                    elif maximum_active_row >= self.numb_rows:
                        maximum_active_row = self.numb_rows - 1
                    active_row_has_changed = (minimum_active_row != prev_row_range[0]) or \
                                             (maximum_active_row != prev_row_range[1])
                    if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                            not (active_row_has_changed or active_col_has_changed or invisible_has_changed):
                        camera.clearHasMoved()
                        continue
                    # left-down, no overlap
                    if maximum_active_col < prev_col_range[0] or minimum_active_row > prev_row_range[1]:
                        # switch to using the activate histeresis (all current is going to be deactivated)
                        maximum_active_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // \
                                             self.cell_size[0]
                        if maximum_active_col >= self.numb_cols:
                            maximum_active_col = self.numb_cols - 1
                        minimum_active_row = (camera_position[1] - activate_range[1]) // self.cell_size[1]
                        if minimum_active_row < 0:
                            minimum_active_row = 0
                        camera.setMovementEnum(CameraMovementEnum.DOWN_LEFT)
                    # left-down, screen overlaps
                    else:
                        camera.setMovementEnum(CameraMovementEnum.DOWN_LEFT_OVERLAP)
                    # update current active row range (after any of the left-down branches)
                    camera.setActiveRowRange([minimum_active_row, maximum_active_row])
                # moved left-up
                elif camera_position[1] < previous_camera_position[1]:
                    maximum_active_row = (camera_position[1] + window_size[1] + deactivate_range[1] - 1) // \
                                         self.cell_size[1]
                    if maximum_active_row > prev_row_range[1]:
                        maximum_active_row = prev_row_range[1]
                    elif maximum_active_row >= self.numb_rows:
                        maximum_active_row = self.numb_rows - 1
                    minimum_active_row = (camera_position[1] - activate_range[1]) // self.cell_size[1]
                    if minimum_active_row > prev_row_range[0]:
                        minimum_active_row = prev_row_range[0]
                    elif minimum_active_row < 0:
                        minimum_active_row = 0
                    active_row_has_changed = (minimum_active_row != prev_row_range[0]) or \
                                             (maximum_active_row != prev_row_range[1])
                    if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                            not (active_row_has_changed or active_col_has_changed or invisible_has_changed):
                        camera.clearHasMoved()
                        continue
                    # left-up, no overlap
                    if maximum_active_col < prev_col_range[0] or maximum_active_row < prev_row_range[0]:
                        # switch to using the activate histeresis (all current is going to be deactivated)
                        maximum_active_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // \
                                             self.cell_size[0]
                        if maximum_active_col >= self.numb_cols:
                            maximum_active_col = self.numb_cols - 1
                        maximum_active_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // \
                                             self.cell_size[1]
                        if maximum_active_row >= self.numb_rows:
                            maximum_active_row = self.numb_rows - 1
                        camera.setMovementEnum(CameraMovementEnum.LEFT_UP)
                    #left-up, screen overlaps
                    else:
                        camera.setMovementEnum(CameraMovementEnum.LEFT_UP_OVERLAP)
                    # update current active row range (after any of the move left-up branches)
                    camera.setActiveRowRange([minimum_active_row, maximum_active_row])
                #only moved left
                else:
                    if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                            not (active_col_has_changed or invisible_has_changed):
                        camera.clearHasMoved()
                        continue
                    # only left no overlap
                    if maximum_active_col < prev_col_range[0]:
                        # switch to using the activate histeresis (all current is going to be deactivated)
                        maximum_active_col = (camera_position[0] + window_size[0] + activate_range[0] - 1) // \
                                             self.cell_size[0]
                        if maximum_active_col >= self.numb_cols:
                            maximum_active_col = self.numb_cols - 1
                        camera.setMovementEnum(CameraMovementEnum.LEFT)
                    # only left screen overlaps
                    else:
                        camera.setMovementEnum(CameraMovementEnum.LEFT_OVERLAP)
                # update current active cell range (after any of the move-left branches)
                camera.setActiveColRange([minimum_active_col, maximum_active_col])
            # only moved down
            elif camera_position[1] > previous_camera_position[1]:
                minimum_active_row = (camera_position[1] - deactivate_range[1]) // self.cell_size[1]
                if minimum_active_row < prev_row_range[0]:
                    minimum_active_row = prev_row_range[0]
                elif minimum_active_row < 0:
                    minimum_active_row = 0
                maximum_active_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // \
                                     self.cell_size[1]
                if maximum_active_row < prev_row_range[1]:
                    maximum_active_row = prev_row_range[1]
                elif maximum_active_row >= self.numb_rows:
                    maximum_active_row = self.numb_rows - 1
                active_row_has_changed = (minimum_active_row != prev_row_range[0]) or \
                                         (maximum_active_row != prev_row_range[1])
                if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                        not (active_row_has_changed or invisible_has_changed):
                    camera.clearHasMoved()
                    continue
                # only down, no overlap
                if minimum_active_row > prev_row_range[1]:
                    # switch to using the activate histeresis (all current is going to be deactivated)
                    minimum_active_row = (camera_position[1] - activate_range[1]) // self.cell_size[1]
                    if minimum_active_row < 0:
                        minimum_active_row = 0
                    camera.setMovementEnum(CameraMovementEnum.DOWN)
                # only down, screen overlap
                else:
                    camera.setMovementEnum(CameraMovementEnum.DOWN_OVERLAP)
                # update current active cell range (after any of the move-down branches)
                camera.setActiveRowRange([minimum_active_row, maximum_active_row])
            # only moved up
            elif camera_position[1] < previous_camera_position[1]:
                maximum_active_row = (camera_position[1] + window_size[1] + deactivate_range[1] - 1) // \
                                     self.cell_size[1]
                if maximum_active_row > prev_row_range[1]:
                    maximum_active_row = prev_row_range[1]
                elif maximum_active_row >= self.numb_rows:
                    maximum_active_row = self.numb_rows - 1
                minimum_active_row = (camera_position[1] - activate_range[1]) // self.cell_size[1]
                if minimum_active_row > prev_row_range[0]:
                    minimum_active_row = prev_row_range[0]
                elif minimum_active_row < 0:
                    minimum_active_row = 0
                active_row_has_changed = (minimum_active_row != prev_row_range[0]) or \
                                         (maximum_active_row != prev_row_range[1])
                if not camera.camera_movement_enum == CameraMovementEnum.INITIALIZED and \
                        not (active_row_has_changed or invisible_has_changed):
                    camera.clearHasMoved()
                    continue
                # up, no overlap
                if maximum_active_row < prev_row_range[0]:
                    # switch to using the activate histeresis (all current is going to be deactivated)
                    maximum_active_row = (camera_position[1] + window_size[1] + activate_range[1] - 1) // \
                                         self.cell_size[1]
                    if maximum_active_row >= self.numb_rows:
                        maximum_active_row = self.numb_rows - 1
                    camera.setMovementEnum(CameraMovementEnum.UP)
                # up, screen overlaps
                else:
                    camera.setMovementEnum(CameraMovementEnum.UP_OVERLAP)
                # update current active cell range (after any of the move-up branches)
                camera.setActiveRowRange([minimum_active_row, maximum_active_row])

        #PART 2: Set the cell states for all cameras
            #There is a hierarchy followed for setting a cell state.
            #Active is higher than Invisibile.  Invisible higher than Inactive
        for camera_id, camera in self._cameras.items():
            if not camera.hasMoved():
                continue
            prev_row_range = camera.getPreviousRowRange()
            prev_col_range = camera.getPreviousColRange()
            row_range = camera.getActiveRowRange()
            col_range = camera.getActiveColumnRange()
            current_invisible_border = camera.getInvisibleBorder()
            #Branches handle deactivating cells
            if camera.camera_movement_enum == CameraMovementEnum.UP:
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.UP_OVERLAP:
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(row_range[1] + 1, prev_row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.UP_RIGHT:
                # deactivate all previous cells
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.UP_RIGHT_OVERLAP:
                # deactivate bottom rectangle
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(row_range[1] + 1, prev_row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
                # deactivate side rectangle
                for col in range(prev_col_range[0], col_range[0]):
                    for row in range(prev_row_range[0], row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT:
                # deactivate all previous cells
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT_OVERLAP:
                # deactivate cells that are out of range
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], col_range[0]):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT_DOWN:
                # deactivate all previous cells
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT_DOWN_OVERLAP:
                # deactivate top rectangle
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], row_range[0]):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
                # deactivate side rectangle
                for col in range(prev_col_range[0], col_range[0]):
                    for row in range(row_range[0], prev_row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN:
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN_OVERLAP:
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], row_range[0]):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN_LEFT:
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN_LEFT_OVERLAP:
                # deactivate top rectangle
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], row_range[0]):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
                # deactivate side rectangle
                for col in range(col_range[1] + 1, prev_col_range[1] + 1):
                    for row in range(row_range[0], prev_row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT:
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT_OVERLAP:
                for col in range(col_range[1] + 1, prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], prev_row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT_UP:
                for row in range(prev_row_range[0], prev_row_range[1] + 1):
                    for col in range(prev_col_range[0], prev_col_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT_UP_OVERLAP:
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(row_range[1] + 1, prev_row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
                # deactivate side rectangle
                for col in range(col_range[1] + 1, prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], row_range[1] + 1):
                        if not self.checkCamerasForVisible(camera_id, row, col):
                            if not self.checkCamerasForActive(camera_id, row, col):
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                            else:
                                self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            #This is removing the camera from the scene and returning cells to state per the change
            elif camera.camera_movement_enum == CameraMovementEnum.DETACH:
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], prev_row_range[1] + 1):
                        if self.checkCamerasForVisible(camera_id, row, col):
                            self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_VISIBLE)
                        elif self.checkCamerasForActive(camera_id, row, col):
                            self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
                        else:
                            self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                continue #done with this phase for detached camera
            elif camera.camera_movement_enum == CameraMovementEnum.SIZE_CHANGE:
                #Check every cell in the previous range, and if it is not in the current range or
                #in range of another camera, deactivate it
                for col in range(prev_col_range[0], prev_col_range[1] + 1):
                    for row in range(prev_row_range[0], prev_row_range[1]+1):
                        if not camera.isInActiveRange(row, col):
                            if not self.checkCamerasForVisible(camera_id, row, col):
                                if not self.checkCamerasForActive(camera_id, row, col):
                                    self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INACTIVE)
                                else:
                                    self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            #Note, an initialized camera will be  CellStateEnum.NO_MOVEMENT, meaning nothing to deactivate
                #The active cells will then be set.
            # set invisibility borders (same loops regardless of camera move direction)
            # left border
            for row in range(row_range[0], current_invisible_border[BOTTOM] + 1):
                for col in range(col_range[0], current_invisible_border[LEFT]):
                    if not self.checkCamerasForVisible(camera_id, row, col):
                        self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            # right border
            for row in range(row_range[0], row_range[1] + 1):
                for col in range(current_invisible_border[RIGHT] + 1, col_range[1] + 1):
                    if not self.checkCamerasForVisible(camera_id, row, col):
                        self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            # top border
            for row in range(row_range[0], current_invisible_border[TOP]):
                for col in range(current_invisible_border[LEFT], current_invisible_border[RIGHT] + 1):
                    if not self.checkCamerasForVisible(camera_id, row, col):
                        self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            # bottom border
            for row in range(current_invisible_border[BOTTOM] + 1, row_range[1] + 1):
                for col in range(col_range[0], current_invisible_border[RIGHT] + 1):
                    if not self.checkCamerasForVisible(camera_id, row, col):
                        self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_INVISIBLE)
            # activate cells (same loops regardless of camera move direction)
            for row in range(current_invisible_border[TOP], current_invisible_border[BOTTOM] + 1):
                for col in range(current_invisible_border[LEFT], current_invisible_border[RIGHT] + 1):
                    self.master_cells[row][col].setCellState(CellStateEnum.CELL_STATE_VISIBLE)

        #PART 3: Transition each changed cell
        for camera_id, camera in self._cameras.items():
            if not camera.hasMoved():
                continue
            prev_row_range = camera.getPreviousRowRange()
            prev_col_range = camera.getPreviousColRange()
            row_range = camera.getActiveRowRange()
            col_range = camera.getActiveColumnRange()
            #Branches handle deactivated cells
            if camera.camera_movement_enum == CameraMovementEnum.UP:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.UP_OVERLAP:
                self.transitionCells((row_range[1]+1, prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.UP_RIGHT:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.UP_RIGHT_OVERLAP:
                # transitions bottom inactive rectangle
                self.transitionCells((row_range[1] + 1, prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
                # transitions side inactive rectangle
                self.transitionCells((prev_row_range[0], row_range[1] + 1),
                                     (prev_col_range[0], col_range[0]))
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT_OVERLAP:
                self.transitionCells((row_range[0], row_range[1] + 1),
                                     (prev_col_range[0], col_range[0]))
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT_DOWN:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.RIGHT_DOWN_OVERLAP:
                # transitions top inactive rectangle
                self.transitionCells((prev_row_range[0], row_range[0]),
                                     (prev_col_range[0], prev_col_range[1] + 1))
                # transitions side inactive rectangle
                self.transitionCells((row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], col_range[0]))
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN_OVERLAP:
                self.transitionCells((prev_row_range[0], row_range[0]),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN_LEFT:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.DOWN_LEFT_OVERLAP:
                # transitions top inactive rectangle
                self.transitionCells((prev_row_range[0], row_range[0]),
                                     (prev_col_range[0], prev_col_range[1] + 1))
                # transitions side inactive rectangle
                self.transitionCells((row_range[0], prev_row_range[1] + 1),
                                     (col_range[1] + 1, prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT_OVERLAP:
                self.transitionCells((row_range[0], row_range[1] + 1),
                                     (col_range[1]+1, prev_col_range[1]+1))
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT_UP:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            elif camera.camera_movement_enum == CameraMovementEnum.LEFT_UP_OVERLAP:
                #transitions bottom inactive rectangle
                self.transitionCells((row_range[1] + 1, prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
                #transitions side inactive rectangle
                self.transitionCells((prev_row_range[0], row_range[1] + 1),
                                     (col_range[1] + 1, prev_col_range[1] + 1))
            #Update the cells that are affected by removing the camera, than remove the camera
            elif camera.camera_movement_enum == CameraMovementEnum.DETACH:
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
                remove_camera_ids.append(camera_id)
                continue
            elif camera.camera_movement_enum == CameraMovementEnum.SIZE_CHANGE:
                #We canvas the entire previous range because there are too many possibilities
                #With a size change (and a possible move).
                self.transitionCells((prev_row_range[0], prev_row_range[1] + 1),
                                     (prev_col_range[0], prev_col_range[1] + 1))
            # transition active cells (same loops regardless of camera move direction)
            self.transitionCells((row_range[0], row_range[1] + 1),
                                 (col_range[0], col_range[1] + 1))

            camera.clearHasMoved()
        return remove_camera_ids

    #the transition call is made after all of the master cell states have been updated
    #Each grid then iterates through the range of changed cells calling their transition method
    #The row/col range are NOT inclusive:
    #row_range[0] to row_range[1] will end at the value one less than row_range[1]
    def transitionCells(self, row_range, col_range):
        for scene_grid in self._scene_grids.values():
            scene_grid.transitionCells(row_range, col_range)

    def update(self):
        try:
            remove_camera_ids = self._updateActiveCells()
            for camera_id in remove_camera_ids:
                self._detachCamera(camera_id)
            #Now update the list of rows which need have cells to update
            self.generateUpdateRows()
        except Exception as e:
            print("Exception caught in MasterGrid update")
            print(e)
