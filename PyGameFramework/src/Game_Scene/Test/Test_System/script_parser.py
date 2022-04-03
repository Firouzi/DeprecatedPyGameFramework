PATH_TO_SCRIPT = "/\\Saved_Scripts\\temp_error.txt"
IDS_TO_KEEP = (320,361)
SKIP_LINES = \
    (
    "choice: 16", "set_random_entity", "SET_ENTITY_ID",
    "choice: 8", "move_sprite_random", " MOVE_SPRITE",
    "choice: 6", "pan_sprite_random", "PAN_SPRITE",
    "entity_remove_random_depend", "REMOVE_ENTITY_DEPENDANT",
    "entity_add_random_depend", "ADD_ENTITY_DEPENDANT"
    )

def IS_ID_TO_KEEP(line):
    for id in IDS_TO_KEEP:
        if " " + str(id) in line:
            return True
    return False

if __name__ == "__main__":
    print("Script parser start")
    source_file = open(PATH_TO_SCRIPT, 'r')
    dest_file = open(PATH_TO_SCRIPT.replace(".txt", "_parsed.txt"), 'w')
    is_save = False
    camera_move_line = True
    cell_state_print = False
    for line in source_file:
        if "*** Update" in line:
            cell_state_print = False
            dest_file.write("\n")
            dest_file.write(line)
            dest_file.write("\n")
        elif "SPRITESTATE " in line:
            dest_file.write(line)
        #We will see the move camera command, then next line will be the location
        elif "move_camera_random" in line or "MOVE_CAMERA" in line:
            dest_file.write(line)
            camera_move_line = True
        elif camera_move_line:
            camera_move_line = False
            dest_file.write(line)
        elif "Previous Camera:" in line:
            cell_state_print = True
            dest_file.write("\n")
            dest_file.write(line)
            #keep pringint the cell state lines, until "Update line" is hit
        elif cell_state_print:
            dest_file.write(line)
        else:
            if "id: " in line or "to entity: " in line or "dependant: " in line:
                #if "id: " + str(ID_TO_KEEP) in line:
                if IS_ID_TO_KEEP(line):
                    is_save = True
                else:
                    is_save = False
            if is_save:
                #trimming out unwanted lines
                keeper = True
                for skip_line in SKIP_LINES:
                    if skip_line in line:
                        keeper = False
                if keeper:
                    dest_file.write(line)
    source_file.close()
    dest_file.close()
    print("Script parser complete")
