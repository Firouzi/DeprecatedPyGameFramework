import random

"""
The purpose of this file was to create the algorithm used in: 
Game_Scene.Scene_Manager.Scene_grid.SceneMasterGrid.generateUpdateRows()

The test here is independant of the src code and the code block was copy pasted over (yuck I know).
The script will generate any number of random camera ranges, and verify that the generateUpdateRows created
a set of row/cols that covered all ranges without duplicates

If changes to the algorithm are needed, they can be sandboxed here before porting to src code
"""

class MOCK_Cam:
    def __init__(self, active_rows, active_cols):
        self.current_active_row_range = active_rows
        self.current_active_col_range = active_cols

def generateUpdateRows(cameras):
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
                    #if overlapping previous range, extend that range
                    if i > 0 and new_col_range[0] <= current_col_ranges[i-1][1]:
                        current_col_ranges[i-1][1] = new_col_range[1]
                    #no overlap on either side, insert it
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
                    #We don't need to overlap the previous range
                    if i > 0 and current_col_ranges[i][0] <= current_col_ranges[i-1][1]:
                        current_col_ranges[i][0] = current_col_ranges[i-1][1] + 1
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

    active_rows = dict()  # {row : [[col_min1, colmax1], [col_min2, col_max2],...]}
    ordered_keys = list()  # list of row ints in ascending order
    for camera in cameras.values():
        col_range = camera.current_active_col_range
        for row in range(camera.current_active_row_range[0], camera.current_active_row_range[1] + 1):
            # If we already have this row, either extend an existing col range, or append it
            if active_rows.get(row) is not None:
                conflateRow(active_rows.get(row), list(col_range))
            else:
                active_rows[row] = [list(col_range)]
                ordered_keys.append(row)
    ordered_keys.sort()
    return ordered_keys, active_rows

def test1():
    print("Test 1 start")
    A = MOCK_Cam([2,5], [3,6])
    B = MOCK_Cam([1,3], [6,10])
    C = MOCK_Cam([3,6], [5,8])
    cameras = {1:A, 2:B, 3:C}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 1 end")
    return [cameras, ordered_keys, active_rows]

def test2():
    print("Test 2 start")
    A = MOCK_Cam([4,7], [8,9])
    B = MOCK_Cam([4,6], [13,15])
    C = MOCK_Cam([5,8], [11,13])
    cameras = {1:A, 2:B, 3:C}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 2 end")
    return [cameras, ordered_keys, active_rows]

def test3():
    print("Test 3 start")
    A = MOCK_Cam([0,2], [0,2])
    B = MOCK_Cam([1,3], [4,5])
    C = MOCK_Cam([0,2], [7,9])
    D = MOCK_Cam([1,4], [9,11])
    cameras = {1:A, 2:B, 3:C, 4:D}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 3 end")
    return [cameras, ordered_keys, active_rows]


def test4():
    print("Test 4 start")
    A = MOCK_Cam([0,2], [8,10])
    B = MOCK_Cam([0,2], [13,15])
    C = MOCK_Cam([2,4], [10,13])
    D = MOCK_Cam([1,5], [15,20])
    cameras = {1:A, 2:B, 3:C, 4:D}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 4 end")
    return [cameras, ordered_keys, active_rows]


def test5():
    print("Test 5 start")
    A = MOCK_Cam([0,1], [0,1])
    B = MOCK_Cam([0,1], [4,5])
    C = MOCK_Cam([0,1], [7,8])
    D = MOCK_Cam([0,1], [10,11])
    E = MOCK_Cam([1,3], [1,12])
    cameras = {1: A, 2:B, 3:C, 4:D, 5:E}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 5 end")
    return [cameras, ordered_keys, active_rows]


def test6():
    print("Test 6 start")
    A = MOCK_Cam([3,5], [5,8])
    B = MOCK_Cam([5,7], [1,3])
    C = MOCK_Cam([5,6], [6,8])
    D = MOCK_Cam([7,8], [2,3])
    E = MOCK_Cam([4,5], [4,5])
    cameras = {1: A, 2:B, 3:C, 4:D, 5:E}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 6 end")
    return [cameras, ordered_keys, active_rows]


def test7():
    print("Test 7 start")
    A = MOCK_Cam([4,9], [9,11])
    B = MOCK_Cam([5,7], [3,5])
    C = MOCK_Cam([6,7], [4,5])
    D = MOCK_Cam([7,8], [5,6])
    E = MOCK_Cam([9,10], [8,12])
    cameras = {1: A, 2:B, 3:C, 4:D, 5:E}
    ordered_keys, active_rows = generateUpdateRows(cameras)
    print(ordered_keys)
    print(active_rows)
    print("Test 7 end")
    return [cameras, ordered_keys, active_rows]

def cameraGenerator(numb_cameras = 3):
    cameras = dict()
    scene_width = random.randint(5,200)
    scene_height = random.randint(5,200)
    for i in range(numb_cameras):
        camera_start_x = random.randint(0, scene_width-1)
        camera_start_y = random.randint(0, scene_height-1)
        camera_width_max = scene_width - camera_start_x
        camera_height_max = scene_height - camera_start_y
        camera_width = random.randint(1,camera_width_max)
        camera_height = random.randint(1,camera_height_max)
        row_range = [camera_start_y, camera_start_y + camera_height - 1]
        col_range = [camera_start_x, camera_start_x + camera_width - 1]
        cameras[i] = MOCK_Cam(row_range, col_range)
    return cameras

def cameraChecker(cameras, ordered_keys, active_rows):
    #print("Camera checker begin")
    is_passing = True
    camera_grids = dict()
    #create a dictionary of every camera {row : {col : bool}}
    #each row/col key pair is a boolean, which will be used to verify entire range is covered
    for camera_id, camera in cameras.items():
        cols = camera.current_active_col_range
        rows =camera.current_active_row_range
        camera_grid = dict()
        for row in range(rows[0], rows[1] + 1):
            grid_row = dict()
            camera_grid[row] = grid_row
            for col in range(cols[0], cols[1] + 1):
                camera_grid[row][col] = False
        camera_grids[camera_id] = camera_grid

    #go through the returned list of row/col ranges, and mark off all cells in cameras
    for row_key in ordered_keys:
        for active_col_range in active_rows[row_key]:
            for col in range(active_col_range[0], active_col_range[1] + 1):
                #At least once camera should contain this cell
                cell_found = False
                for camera_id, camera_grid in camera_grids.items():
                    cell_row = camera_grid.get(row_key)
                    cell = None
                    if cell_row is not None:
                        cell = cell_row.get(col)
                    if cell is not None:
                        cell_found = True
                        if cell:
                            print("Duplicate coverage detected")
                            is_passing = False
                            print(row_key,active_col_range,col,camera_id)
                        camera_grid[row_key][col] = True
                if not cell_found:
                    print("Cell not found")
                    is_passing = False
                    print(row_key, active_col_range, col)

    #iterate back through camera grids and verify all booleans are True
    for camera_id, camera_grid in camera_grids.items():
        for row_numb, grid_row in  camera_grid.items():
            for col_numb, col in grid_row.items():
                if not col:
                    print("False col found")
                    is_passing = False
                    print(camera_id,row_numb,col_numb)

    #print("Camera checker complete")

    if is_passing:
        pass
        #print("PASS")
    else:
        print("FAIL")

def randomTest(numb_cameras = 3):
    #print("Random test begin")
    cameras = cameraGenerator(numb_cameras)
    ordered_keys, active_rows = generateUpdateRows(cameras)
    cameraChecker(cameras, ordered_keys, active_rows)
    #print("Random test end")

if __name__ == "__main__":
    print("Test Camera_Row begin")
    for i in range(500000):
        randomTest(numb_cameras=random.randint(1,60))
        if i%100==0:
            print(i)


    print("Test Camera_Row end")