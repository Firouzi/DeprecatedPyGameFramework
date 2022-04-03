
#(7.1) Camera within world boundary
#(7.2) Camera only part of 1 scene
#(7.3) Camera ID matches CameraManagers ID
#(7.4) Camera Scene reference is correct
#(7.5) has moved flag is cleared after update
def _testCameraWithinWorldBoundary_(game_engine_mock):
    try:
        camera_manager = game_engine_mock._camera_manager
        scene_manager = game_engine_mock._scene_manager
        for camera_id, camera in camera_manager._cameras.items():
            if camera.camera_id != camera_id: #(7.3)
                print("test_Scene_camera - camera id mismatch, id: " + str(camera_id))
                print(camera.camera_id)
                assert False
            __checkScenesForCamera__(scene_manager, camera_id, camera) #(7.2), #(7.3), #(7.4)
            if camera.scene is None:
                continue
            if not camera.scene.is_active: #We don't update inactive scenes
                continue
            if camera._has_moved.value: #(7.5)
                print("test_Scene_camera - has moves flag not cleared, id:" + str(camera_id))
                assert False
            #(7.1)
            camera_position = camera._position
            world_size = camera.world_size
            if camera_position[0] < 0:
                print("test_Scene_camera - position X is negative, id: " + str(camera_id))
                assert False
            if camera_position[0] >= world_size[0]:
                print("test_Scene_camera - position X is larger than world size, id: " + str(camera_id))
                assert False
            if camera_position[1] < 0:
                print("test_Scene_camera - position X is negative, id: " + str(camera_id))
                assert False
            if camera_position[1] >= world_size[1]:
                print("test_Scene_camera - position Y is larger than world size, id: " + str(camera_id))
                assert False
    except Exception as e:
        print(e)
        return False
    return True

### HELPER FUNCTIONS ###

def __checkScenesForCamera__(scene_manager, camera_id, camera):
    try:
        camera_found = False
        for scene in scene_manager._scenes.values():
            for scene_camera_id, scene_camera in scene._cameras.items():
                if scene_camera_id == camera_id:
                    if camera_found:
                        print("test_Scene_camera - duplicate camera id found across scenes: " + str(camera_id))
                        assert False
                    camera_found = True
                    if camera != scene_camera:
                        print("test_Scene_camera - camera reference mismatches scene reference, id: " + str(camera_id))
                        assert False
                    if camera.scene is None:
                        print("test_Scene_camera - camera found in scene without scene reference, id:" + str(camera_id))
                        assert False
                    elif camera.scene != scene:
                        print("test_Scene_camera - camera scene reference mismatch, id:" + str(camera_id))
                        assert False
        if not camera_found and camera.scene is not None:
            print("test_Scene_camera - did not find the camera in any scene, id: " + str(camera_id))
            assert False
    except Exception as e:
        print(e)
        assert False
