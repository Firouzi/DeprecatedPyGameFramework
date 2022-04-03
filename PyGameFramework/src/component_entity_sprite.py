from component_system import EntityComponent, EntityComponentSystem, Renderable, Component
import sys
sys.path.append("parameters\\")
import GRAPHICS_PARAM

VALUES_PER_FRAME = 4 #x, y, width, height

class SpriteInstance(Renderable):
    #PhysicsComponentSystem.getOrientation(entity_id : int, particle_index : int)
    get_orientation = None
    #PhysicsComponentSystem.getPosition(entity_id : int, particle_index : int)
    get_position = None
    #PhysicsComponentSystem.getVelocity(entity_id : int, particle_index : int)
    get_velocity = None

    TILE_SIZE = 32 #TODO - need to get the tile_size of the current map

    def __init__(self,
                 parent_component, #Component
                 component_element_id,  #int
                 layer_level_id,
                 subcomponent_index,  #int
                 sprite_data): #*SpriteData):
        super(SpriteInstance, self).__init__(parent_component = parent_component,
                                             component_element_id = component_element_id,
                                             layer_level_id = layer_level_id,
                                             subcomponent_index = subcomponent_index)
        self._sprite_data = sprite_data
        self._image = sprite_data.image
        self._frames = sprite_data.frames
        self._num_frames = sprite_data.num_frames
        self._is_eightway = sprite_data.is_eightway
        self._frame_times_ms = sprite_data.frame_times_ms

        self._image_coordinates = [0, 0, 0, 0]
        self._screen_coordinates = [0, 0, 0]
        self._world_coordinates = [0,0,0] #The pixel position of top left corner in world map
        self._is_active = False

        #updated by SpriteComponent
        self._current_behavior_state = None
        self._particle_ptr = None #note - this is not Ptr class, it is the actual Particle

    def setParticlePtr(self,
                       particle_ptr): #Particle
        self._particle_ptr = particle_ptr

    def updateBehaviorState(self,
                            behavior_state): #BehaviorStateBase
        self._current_behavior_state = behavior_state

    def calculateCoordinates(self,
                             camera_offset, #[int, int]
                             lag_normalized): #float [0,1)
        #calculate image frame to render
        current_frame_number = self._current_behavior_state.getCurrentFrameIndex()
        #Need to calculate sprite direction from this
        orientation = self._particle_ptr.getOrientation()
        direction_multiplier = 1
        frame_index = (current_frame_number + (self._num_frames * direction_multiplier)) * VALUES_PER_FRAME
        assert(current_frame_number <self._sprite_data.num_frames)
        #calculate coordinates of image to render
        self._image_coordinates = self._frames[frame_index: frame_index + VALUES_PER_FRAME]
        #calculate position to render on screen
        velocity = self._particle_ptr.getVelocity()
        self._world_coordinates = self._particle_ptr.getPosition()
        self._screen_coordinates = [self._world_coordinates[0] + velocity[0] * lag_normalized - camera_offset[0],
                                    self._world_coordinates[1] + velocity[1] * lag_normalized - camera_offset[1],
                                    self._world_coordinates[2] + velocity[2] * lag_normalized]

    def getFrameTimesMs(self):
        return self._frame_times_ms

    def getImage(self):
        return self._image

    def getImageCoordinates(self):
        return self._image_coordinates

    def getScreenCoordinates(self):
        return self._screen_coordinates

    def getWorldCoordinates(self):
        return self._world_coordinates #[int, int, int]

    #We will add the Y height to the world coordinates to make get the bottom of the sprite
    #Returns bottom left pixel position
    def getGroundPositionPx(self):
        return [self._world_coordinates[0] + self._image_coordinates[2],  #left side of sprite
                self._world_coordinates[1] + self._image_coordinates[3],  #Bottom of the sprite
                self._world_coordinates[2]] #Z

    def isTilemap(self):
        return False #Boolean

    def getTilePosition(self):
        position = SpriteInstance.get_position(entity_id = self.component_element_id,
                                               particle_index = self.subcomponent_index)
        return [position[0]//GRAPHICS_PARAM.TILE_SIZE[0],
                position[1]//GRAPHICS_PARAM.TILE_SIZE[1],
                position[2]//GRAPHICS_PARAM.TILE_SIZE[2]]

#functionally equivalent to the SpriteInstanceexcept for getGroundPositionPx()
#Calls the parent_component to getGroundPosition (which will return the value from the main sprite instances)
class SpriteInstanceChild(SpriteInstance):
    def __init__(self,
                 parent_component, #Component
                 component_element_id,  #int
                 layer_level_id,
                 subcomponent_index,  #int
                 sprite_data): #*SpriteData):
        super(SpriteInstanceChild, self).__init__(parent_component = parent_component,
                                                  component_element_id = component_element_id,
                                                  layer_level_id = layer_level_id,
                                                  subcomponent_index = subcomponent_index,
                                                  sprite_data = sprite_data)

    #The sprite is broken up into multiple pieces, but only has 1 ground position.
    #We want to ge the ground position of the parent sprite, this will allow sprites to
    #be rendered in the correct order, making background and foreground renderables show correctly
    def getGroundPositionPx(self):
        return self.parent_component.getGroundPositionPx()


class EntitySpriteComponent(EntityComponent):
    #BehaviorComponentSystem.setBehaviorStateFrameTimes
    set_behavior_state_frame_times = None #(behavior_FSM_index : int, behavior_state_id : int, frame_times_ms : [int])

    def __init__(self,
                 entity_element_id,  #int
                 layer_level_id,
                 sprite_instances_list):  #({behavior_state_id : SpriteInstance},)
        super(EntitySpriteComponent, self).__init__(entity_element_id = entity_element_id,
                                                    layer_level_id = layer_level_id)
        self.sprite_instances_list = sprite_instances_list
        #These pointers will refelect the current behavior state for each subcomponent index
        #They will be updated by the SpriteComponentSystem.requestPointers() call
        self._current_behavior_state_ptrs = list()

        #particle ptrs used to get kinamatic data
        self._particle_ptrs = list() #Note - Ptr class not used.  These are directly the particles

        #The current ID's tracks the active behavior state ID for each subcomponent
        #Each update we check for and update the active behavior state for each subcomponent
        #If the active ID has changed, set that renderable to inactive and mark the new one active
        self._current_behavior_ids = list()

        #Current sprites will be a list of ptrs which will be sent to renderable layer
        #There is one Ptr for each subcomponent, although there are more than 1 sprite_instances per subcomponent
        #The current_sprite_instance Ptr corresponds to current state, and is updated in the Ptr
        self._current_sprite_ptrs = list()

    #need to call this to setup the sprite_pointers and behavior state
    def initialize(self):
        self.sprite_instances_list = tuple(self.sprite_instances_list)
        self._current_sprite_ptrs = list() #This is redundant, but PyCharm seems to need it to prevent a warning
        #We create the list of current_behavior id's arbitrarily
        #We don't need to know the correct active one now, we will update it before we render
        for sprite_instances_list in self.sprite_instances_list:
            behavior_state_keys = list(sprite_instances_list.keys())
            self._current_behavior_ids.append(behavior_state_keys[0])
            # OK, now we need to make 1 sprite active for each subcomponent
            sprite_instance = sprite_instances_list[behavior_state_keys[0]]
            sprite_instance.activate()
            #As we change the active sprite, we can update the Ptr class with the new sprite
            #The render layer will keep thr Ptr class reference, and then see the new sprite
            ptr = Component.request_ptr(self.layer_level_id) #Get a Ptr (wrapper class)
            ptr.set(sprite_instance)
            self._current_sprite_ptrs.append(ptr) #set the Ptr with this sprite instance
        #This will help ensure that we don't make an unintended type of change
        self._current_sprite_ptrs = tuple(self._current_sprite_ptrs)

        #Set all of the behavior id's to an invalid index to start
        #This will ensure that we will update on the first call.
        index = 0
        while index < len(self._current_behavior_ids):
            self._current_behavior_ids[index] = -1
            index+=1

    #All sprite_instanced not in the current_sprite_ptrs list should already be inactive
    #We only have a 1d list of _current_sprite_ptrs (1 entry per subcomponent).  Free all of those
    def kill(self):
        self.deactivate()
        for sprite_ptr in self._current_sprite_ptrs:
            sprite_ptr.deactivate() #don't render me
            sprite_ptr.free() #now you can reuse my Ptr wrapper

    #We requested the Ptr wrappers from the SceneHandler, now we send back the Ptrs
    #initialized with the sprite_instances
    def getRenderables(self):
        return self._current_sprite_ptrs

    #This is being called by the sprite_instance which is a child sprite
    #We want the ground position only from a parent sprite, which will be index 0 for our active sprites
    def getGroundPositionPx(self):
        return self._current_sprite_ptrs[0].getGroundPositionPx()

    def update(self):
        #loop goes through each subcomponent index, getting the current behavior state
        #the behavior state is needed to update the currentframe for the sprite instance
        for behavior_FSM_index in range(len(self._current_behavior_ids)): #count number of subcomponents
            behavior_state = self._current_behavior_state_ptrs[behavior_FSM_index].get()
            #Compare the behavior state ID to the last time to see if it has changed
            #If it has changed, deactivate the old sprite and activate the new one
            prev_behavior_id = self._current_behavior_ids[behavior_FSM_index]
            new_behavior_id = behavior_state.getBehaviorId()
            if prev_behavior_id != new_behavior_id: #we had a state change
                #TODO - changing behavior state doesn't always mean a new sprite
                #TODO - Chceck to see if the sprite will change FIRST
                self._current_sprite_ptrs[behavior_FSM_index].deactivate()
                self._current_behavior_ids[behavior_FSM_index] = new_behavior_id
                #update the current sprite reference for this subcomponent index
                current_sprite = self.sprite_instances_list[behavior_FSM_index][new_behavior_id]
                current_sprite.activate()
                self._current_sprite_ptrs[behavior_FSM_index].set(current_sprite)
                self._current_sprite_ptrs[behavior_FSM_index].updateBehaviorState(behavior_state)

    #We will update the list of ptrs to the behavior states
    #Update each behavior state with the SpriteInstances Frame Timer
    def setBehaviorStatePtrs(self,
                             behavior_state_ptrs):
        self._current_behavior_state_ptrs = behavior_state_ptrs
        numb_subcomponents = len(self.sprite_instances_list)
        behavior_FSM_index = 0
        while behavior_FSM_index < numb_subcomponents:
            for behavior_state_id, sprite_instance in self.sprite_instances_list[behavior_FSM_index].items():
                EntitySpriteComponent.set_behavior_state_frame_times(entity_id = self.getEntityId(),
                                                                     behavior_FSM_index = behavior_FSM_index,
                                                                     behavior_state_id = behavior_state_id,
                                                                     frame_times_ms = sprite_instance.getFrameTimesMs())
            behavior_FSM_index+=1


    def setParticlePtrs(self,
                        particle_ptrs):
        self._particle_ptrs = particle_ptrs
        index = 0
        for sprite_instances in self.sprite_instances_list:
            for behavior_state_id in sprite_instances.keys():
                sprite_instances[behavior_state_id].setParticlePtr(particle_ptrs[index])
            index +=1

class SpriteComponentSystem(EntityComponentSystem):
    receive_behavior_state_ptrs = None
    receive_particle_ptrs = None

    def __init__(self):
        super(SpriteComponentSystem, self).__init__()
        self._entity_sprite_components = dict() #{id : EntitySpriteComponent}

    def getSceneComponents(self,
                           component_element_id):
        try:
            return self._entity_sprite_components[component_element_id].getRenderables()
        except:
            return list() #empty set if there is no element with this id

    def removeComponent(self,
                        component_element_id): #int
        try:
            self._entity_sprite_components[component_element_id].kill()
            del self._entity_sprite_components[component_element_id]
            return True
        except:
            return False

    def createComponent(self,
                        component_element_id,  #int
                        layer_level_id,
                        resource_data): #SpriteResourceData
        #We will change this to the SpriteInstanceChild type after the first loop
        #Child sprites refer to the parent component to get the GroundPosition of a sprite
        sprite_instance_type = SpriteInstance
        #2d array - we need a row per subcomponent, and a column per behavior state
        sprite_instances_lists = list()
        #We need to create the parent first, because each instance needs to get
        #a reference to the parent
        entity_sprite_component = EntitySpriteComponent(
            entity_element_id= component_element_id,
            layer_level_id = layer_level_id,
            sprite_instances_list= sprite_instances_lists)

        sub_component_index = 0
        for sprite_instance_datas in resource_data.sprite_instance_datas_list:
            spite_instances = dict()  # {behavior_state_id : *SpriteInstance}
            for sprite_instance_data in sprite_instance_datas:
                #The first set of sprite_instance_datas will create SpriteInstance's
                sprite_instance = sprite_instance_type(parent_component = entity_sprite_component,
                                                       component_element_id =component_element_id,
                                                       layer_level_id = layer_level_id,
                                                       subcomponent_index = sub_component_index,
                                                       sprite_data = sprite_instance_data.sprite_data)
                #we can have multiple ID's hash to the same SpriteInstance
                #this is just a pointer so we aren't too worried about the copied data
                for behavior_state_id in sprite_instance_data.behavior_state_ids:
                    spite_instances[behavior_state_id] = sprite_instance
            #The rest of the subcomponents are the children sprites, they call the parent component for GroundPosition
            sprite_instance_type = SpriteInstanceChild
            sub_component_index+=1
            sprite_instances_lists.append(spite_instances)

        entity_sprite_component.initialize()
        self._entity_sprite_components[component_element_id] = entity_sprite_component

    def requestPointers(self,
                        component_element_id):
        try:
            behavior_state_ptrs = SpriteComponentSystem.receive_behavior_state_ptrs(component_element_id)
            particle_ptrs = SpriteComponentSystem.receive_particle_ptrs(component_element_id)
            self._entity_sprite_components[component_element_id].setBehaviorStatePtrs(behavior_state_ptrs)
            self._entity_sprite_components[component_element_id].setParticlePtrs(particle_ptrs)
            return True
        except:
            return False


    def update(self):
        for entity_sprite_component in self._entity_sprite_components.values():
            entity_sprite_component.update()
