from resource_management_scene import SCENE_LAYER_TYPE
from utility import PtrPool, RenderablePtrPool
import sys
sys.path.append("parameters\\")
import FUNCTIONAL_PARAM

class SceneLayerFactory:
    def __init__(self):
        pass

    def createSceneLayer(self,
                         layer_element_id, #int
                         layer_level_id, #int
                         resource_data): #ResourceData
        if resource_data.scene_layer_type == SCENE_LAYER_TYPE.RENDERABLE:
            return RenderLayer(layer_element_id = layer_element_id,
                               layer_level_id = layer_level_id,
                               scene_layer_type = resource_data.scene_layer_type,
                               renderable_layer_type = resource_data.renderable_layer_type,
                               tile_perspective = resource_data.tile_perspective,
                               is_needs_sorting = resource_data.is_needs_sorting)
        elif resource_data.scene_layer_type ==  SCENE_LAYER_TYPE.PHYSICAL:
            pass
        elif resource_data.scene_layer_type ==  SCENE_LAYER_TYPE.ENVIRONMENT:
            pass
        elif resource_data.scene_layer_type ==  SCENE_LAYER_TYPE.EVENT:
            pass

class SceneLayer:
    def __init__(self,
                 layer_element_id, #int
                 layer_level_id, #int
                 scene_layer_type): #SCENE_LAYER_TYPE
        self.layer_element_id = layer_element_id
        self.layer_level_id = layer_level_id
        self.scene_layer_type = scene_layer_type

        #If we made this a dict, removal would be easy, O(1). However, we will
        #be sorting this list often, which would add an O(N) operation of converting
        #the dict to a list first.  Furthemore, may use more advanced data structures in the future
        self._components = list() #[Component]
        self._is_active = True #bool
        self._ptr_pool = None #explicitly name the object here, but init it in the func call
        self._initializePtrPool()

    def _initializePtrPool(self):
        self._ptr_pool = PtrPool(pool_size = FUNCTIONAL_PARAM.PTR_POOL_SIZE)

    #These may be ptr-wrapped components, or Components (this class does not care)
    def addComponent(self,
                     component): #Component
        #Ptrs can be reused, if we already have the Ptr in the list, we don't want to add it again
        if not component.isInScene():
            self._components.append(component)
            component.setInScene(True)

    def activate(self):
        self._is_active = True
    def deactivate(self):
        self._is_active = False
    def isActive(self):
        return self._is_active
    def requestPtr(self):
        return self._ptr_pool.requestPtr()

class RenderLayer(SceneLayer):
    def __init__(self,
                 layer_element_id, #int
                 layer_level_id, #int
                 scene_layer_type, #SCENE_LAYER_TYPE
                 renderable_layer_type, #RENDERABLE_LAYER_TYPE
                 tile_perspective,
                 is_needs_sorting):
        super(RenderLayer, self).__init__(layer_element_id = layer_element_id,
                                          layer_level_id = layer_level_id,
                                          scene_layer_type = scene_layer_type)
        self.renderable_layer_type = renderable_layer_type #RENDERABLE_LAYER_TYPE
        self._tile_perspective = tile_perspective
        self._is_needs_sorting = is_needs_sorting

    #Overridden so that we get RenderablePtrs
    def _initializePtrPool(self):
        self._ptr_pool = RenderablePtrPool(pool_size = FUNCTIONAL_PARAM.PTR_POOL_SIZE)

    def isNeedsSorting(self):
        return self._is_needs_sorting


    #Calls the update methods for all renderables, and sorts them if needed
    def updateRenderableCoordinates(self,
                                    camera_offset, #[int, int]
                                    lag_normalized): #float [0.0,1.0)
        self._calculateCoordinates(camera_offset = camera_offset,
                                   lag_normalized = lag_normalized)
        if self._is_needs_sorting:
            self._sort()


    #has every renderable update it's position based on the current camera and lag, ignores inactive components
    def _calculateCoordinates(self,
                              camera_offset, #[int, int]
                              lag_normalized): #float [0.0,1.0)
        for renderable in self._components:
            if not renderable.isActive():
                continue
            renderable.calculateCoordinates(camera_offset = camera_offset,
                                            lag_normalized = lag_normalized)

    #implements insertion sort, based on Y position of renderable, ignores inactive components
    def _sort(self): #TODO - add the Z component?
        for i in range(1, len(self._components)):
            if not self._components[i].isActive():
                continue #We are not going to sort inactive components
            key = self._components[i]
            j = i - 1
            skips = 0 #This lets us ignore any indexes which contain inactive components
            #Sort on the Y position of the renderable
            while j >= 0:# and key.getGroundPositionPx()[1] < self._components[j].getGroundPositionPx()[1]:
                if not self._components[j].isActive():
                    skips +=1
                elif key.getGroundPositionPx()[1] < self._components[j].getGroundPositionPx()[1]:
                    self._components[j+1+skips] = self._components[j]
                    skips = 0 #we have jumped that portion of the array
                else: #The subarray is sorted now
                    break
                j -= 1
            self._components[j+1+skips] = key

    def getRenderables(self):
        return self._components