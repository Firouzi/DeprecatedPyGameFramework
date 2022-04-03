class ComponentSystem:
    def __init__(self):
        pass

    def update(self):
        pass

    #Returns either the actual components, or components wrapped in a ptr
    #Wrapped components are used to be able to change components without the client being aware
    def getSceneComponents(self,
                           component_element_id): #int
        return list() #if nothing needed for scene layer element, return empty set

    #tell Component system to call any of the methods which update needed pointers
    #this will provide a reference to an object for easier access without needing to query the system
    #These are callbacks and ptrs that the ComponentSystem recieves
    def requestPointers(self,
                        component_element_id): #int
        pass

    def removeComponent(self,
                        component_element_id): #int
        pass

class EntityComponentSystem(ComponentSystem):
    def __init__(self):
        super(EntityComponentSystem, self).__init__()

    def createComponent(self,
                        component_element_id,  # int - dynamic id for this component
                        layer_level_id, #int
                        resource_data): #ResourceData
        pass

class SceneComponentSystem(ComponentSystem):
    def __init__(self):
        super(SceneComponentSystem, self).__init__()

    def createComponent(self,
                        component_element_id,  # int - dynamic id for this component
                        layer_element_id,  # int - dynamic id for the entire layer
                        layer_level_id,  # int  - the layer level this component is part of
                        resource_data):  # ResourceData
        pass

class Component:
    #Gets a Ptr wrapper from the SceneLayer which will be returned with this Component
    request_ptr = None #SceneHandler.requestPtr(layer_level_id : int)

    def __init__(self,
                 component_element_id,  # int - dynamic id for this component
                 layer_level_id): #int
        self.component_element_id = component_element_id
        self.layer_level_id = layer_level_id

        self._is_active = True
        self.tag_id = 0 # default is 0, or no tag
        # SceneLayer needs to track if it has already added this Component
        #This is mostly to mimmick the needed functionality in the class Ptr.
        self._is_in_scene = False

    #when we add this component to the scene_layer, flag it as added
    #if already added it previously, scene layer doesn't need to re-add it.
    def setInScene(self,
                   is_in_scene = True):
        self._is_in_scene = is_in_scene

    def isInScene(self):
        return self._is_in_scene

    def update(self):
        pass

    def activate(self):
        self._is_active = True

    def deactivate(self):
        self._is_active = False

    def isActive(self):
        return self._is_active

    def getElementId(self):
        return self.component_element_id

    def getLayerLevelId(self):
        return self.layer_level_id

    #Ground level is the pixel the entire component is 'touching the ground' at, and is used to calculate order of rendering
    #All subcomponents would chare the same ground position
    def getGroundPositionPx(self):
        return [0,0,0]

    #not required but should be called on components after constructing them if needed
    def initialize(self):
        pass

    #Similar to invoking a destructor, should free up all resources component is utilizing
    #and deactive/free any Subcomponent's/Ptr's it owns
    def kill(self):
        pass


class Subcomponent(Component):
    def __init__(self,
                 parent_component, #This is the component which would have this subcomponent in it's list
                 component_element_id,  #int
                 layer_level_id, #int
                 subcomponent_index): #int
        super(Subcomponent, self).__init__(component_element_id = component_element_id,
                                           layer_level_id = layer_level_id)
        self.parent_component = parent_component
        self.layer_level_id = layer_level_id
        self.subcomponent_index = subcomponent_index

    def getSubcomponentIndex(self):
        return self.subcomponent_index

    def getGroundPositionPx(self):
        return [0,0,0]


class EntityComponent(Component):
    def __init__(self,
                 entity_element_id, #int dynamic id for the entity
                 layer_level_id): #int
        super(EntityComponent, self).__init__(component_element_id = entity_element_id,
                                              layer_level_id = layer_level_id)

    def getEntityId(self):
        return self.component_element_id

class SceneComponent(Component):
    def __init__(self,
                 scene_element_id, # int - dynamic id for this component
                 layer_element_id,  # int - dynamic id for the entire layer
                 layer_level_id):  # int - the layer level this component is a part of
        super(SceneComponent, self).__init__(component_element_id = scene_element_id,
                                             layer_level_id = layer_level_id)
        self.layer_element_id = layer_element_id
        self.layer_level_id = layer_level_id

#Each renderable should only send 1 image per update.
#The returned coordinates or pixel positions can send back multiple blocks to draw
#len(coordinates)/4 should equal len(position)/3
class Renderable(Subcomponent):
    def __init__(self,
                 parent_component,#Component
                 component_element_id,
                 layer_level_id,
                 subcomponent_index):
        super(Renderable, self).__init__(parent_component = parent_component,
                                         component_element_id=component_element_id,
                                         layer_level_id = layer_level_id,
                                         subcomponent_index = subcomponent_index)

    def getImage(self):
        return None #pygame.image

    #Tell the renderer to prepare it's image, coordinate and position values
    #The next calls will pull those values
    def calculateCoordinates(self,
                             camera_offset, #[int, int]
                             lag_normalized): #float [0,1)
        pass

    #return the portion(s) of the image to draw.
    #should be in sets of 4 ints, x,y,width,height
    def getImageCoordinates(self):
        return [0,0,0,0] #[int]

    def getTilePosition(self):
        return [0,0,0] #[int, int, int]

    def getWorldCoordinates(self):
        return [0,0,0] #[int, int, int]

    #The x,y,z position of the renderable
    #returned in groups of 3
    def getScreenCoordinates(self):
        return [0,0,0] #[int, int, int]