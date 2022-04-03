from Test_condition_manager import TestConditionContainer, TestCondition

#Look for conditions a node is in based on it's state
class SceneStateConditionContainer(TestConditionContainer):
    def __init__(self, scene_test_conditions):
        super(SceneStateConditionContainer, self).__init__(scene_test_conditions)
        self.name = "Scene State Container"

    def isRunContainer(self):
        return not self.isMet()

    #params should be a list of sprites, or do you break that out at this point?
    def runContainer(self, game_engine):
        for scene_test_condition in self.test_conditions:
            if not scene_test_condition.isMet():
                scene_test_condition.testCondition(game_engine._scene_manager)

#is met when a minimum number of active and inactive scenes exist
class SceneCountCondition(TestCondition):
    def __init__(self, test_conditions, num_active, num_inactive):
        super(SceneCountCondition, self).__init__(test_conditions)
        self.num_active = num_active
        self.num_inactive = num_inactive
        self.name = "Scene Count Condition - " +str(num_active) +", " + str(num_inactive)

    def selfTest(self, scene_manager):
        if len(scene_manager._active_scenes) >= self.num_active:
            if len(scene_manager._scenes) - len(scene_manager._active_scenes) >= self.num_inactive:
                return True
        return False

#is met when a minimum number of layers in a scene exist
class LayerCountCondition(TestCondition):
    def __init__(self, test_conditions, min_layers):
        super(LayerCountCondition, self).__init__(test_conditions)
        self.min_layers = min_layers
        self.name = "Layer Count Condition - " + str(min_layers)

    def selfTest(self, scene_manager):
        for scene in scene_manager._active_scenes.values():
            if len(scene._scene_layers) >= self.min_layers:
                return True
        return False

#is met when a minimum number of cameras in exist, and in cameras in 1 scene
class CameraCountCondition(TestCondition):
    def __init__(self, test_conditions, total_cams, scene_cams):
        super(CameraCountCondition, self).__init__(test_conditions)
        self.total_cams = total_cams
        self.scene_cams = scene_cams
        self.name = "Camera Count Condition - " + str(total_cams) + ", " + str(scene_cams)

    def selfTest(self, scene_manager):
        cam_count = 0
        min_scene_met = False
        for scene in scene_manager._active_scenes.values():
            cam_count += len(scene._cameras)
            if len(scene._cameras) >= self.scene_cams:
                min_scene_met = True
        if cam_count >= self.total_cams and min_scene_met:
            return True
        return False

#is met when a minimum number of nodes exist in a scene, a cell, and in offscreen actives
class NodeCountCondition(TestCondition):
    def __init__(self,
                 test_conditions,
                 nodes_in_scene,
                 offscreen_actives, #in grid
                 aa_inv_ether_nodes, #in grid
                 vis_nodes_in_cell,
                 inv_nodes_in_cell,
                 inv_eth_nodes_in_cell):
        super(NodeCountCondition, self).__init__(test_conditions)
        self.nodes_in_scene = nodes_in_scene
        self.offscreen_actives = offscreen_actives
        self.aa_inv_ether_nodes = aa_inv_ether_nodes
        self.vis_nodes_in_cell = vis_nodes_in_cell
        self.inv_nodes_in_cell = inv_nodes_in_cell
        self.inv_eth_nodes_in_cell = inv_eth_nodes_in_cell

        self.name = "Node Count Condition"

    def selfTest(self, scene_manager):
        for scene in scene_manager._active_scenes.values():
            if len(scene._sprites) >= self.nodes_in_scene:
                for layer in scene._scene_layers.values():
                    if len(layer.scene_grid.offscreen_active_nodes) >= self.offscreen_actives and \
                            len(layer.scene_grid.always_active_invisible_ethereal_nodes) >= self.aa_inv_ether_nodes:
                        #If true to this point, see if we meet the min node in a cell count
                        if self._nodeCount(layer.scene_grid):
                            return True
        return False

    def _nodeCount(self, grid):
        for row in grid._scene_cells:
            for cell in row:
                if len(cell.invisible_ethereal_nodes) >= self.inv_eth_nodes_in_cell:
                    if self._visibleCount(cell) and self._invisibleCount(cell):
                        return True
        return False

    def _visibleCount(self, cell):
        count = 0
        current = cell.head
        while current is not None:
            count+=1
            current = current.next_node
        if count >= self.vis_nodes_in_cell:
            return True
        return False

    def _invisibleCount(self, cell):
        count = 0
        current = cell.invisible_head
        while current is not None:
            count += 1
            current = current.next_node
        if count >= self.inv_nodes_in_cell:
            return True
        return False

#return a list of all scene_state test containers
def buildSceneStateContainers():
    scene_test_conditions = list()
    containers = list()
    scene_test_conditions.append(SceneCountCondition(None, 5,5))
    scene_test_conditions.append(LayerCountCondition(None, 10))
    scene_test_conditions.append(CameraCountCondition(None, 6, 4))
    scene_test_conditions.append(NodeCountCondition(None, 100, 10, 3, 5, 5, 2))
    scene_state_condition_container = SceneStateConditionContainer(scene_test_conditions)
    containers.append(scene_state_condition_container)
    return containers
