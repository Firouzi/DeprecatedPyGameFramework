from enum import Enum
from component_entity_physics import ParticleData
import json
from resource_management import ResourceData, ResourceManager

#resource data filepaths
ENTITY_ROOT_PATH = 'resource\\entity\\'
ENTITY_FILENAME_TAG = 'entity_'

ENTITY_BEHAVIOR_PATH = 'behavior\\'
BEHAVIOR_FILENAME_TAG = 'behavior_'

ENTITY_PHYSICS_PATH = 'physics\\'
PHYSICS_FILENAME_TAG = 'physics_'

ENTITY_SPRITE_PATH = 'sprite\\'
SPRITEDATA_FILENAME_TAG = 'spritedata_'

SPRITE_BEHAVIOR_INDEX = 0
SPRITE_DATA_INDEX = 1

class ERESOURCE_DATA_TYPE(Enum):
    UNKNOWN = 0
    BEHAVIOR = 1
    PHYSICS = 2
    SPRITE = 3

#generic container
class EntityResourceData(ResourceData):
    def __init__(self,
                 e_resource_id, #int
                 e_resource_data_type): #ERESOURCE_DATA_TYPE
        super(EntityResourceData, self).__init__()
        self.e_resource_id = e_resource_id
        self.e_resource_data_type = e_resource_data_type

class EntityDataCollection:
    def __init__(self,
                 e_resource_collection_id,  # int
                 e_resource_ids):  # {ERESOURCE_DATA_TYPE : int} - We only will have 1 EntityResourceData per EntityComponentType
        self.e_resource_collection_id = e_resource_collection_id
        self.e_resource_ids = e_resource_ids

#Container class for SpriteResourceData
class SpriteInstanceData:
    def __init__(self,
                 behavior_state_ids, #[int]
                 sprite_data): #*SpriteData
        self.behavior_state_ids = behavior_state_ids
        self.sprite_data = sprite_data

class SpriteResourceData(EntityResourceData):
    def __init__(self,
                 e_resource_id, #int
                 sprite_instance_datas_list): #((SpriteInstanceData,),)]
        super(SpriteResourceData, self).__init__(e_resource_id, ERESOURCE_DATA_TYPE.SPRITE)
        self.sprite_instance_datas_list = sprite_instance_datas_list

class PhysicsResourceData(EntityResourceData):
    def __init__(self,
                 e_resource_id, #int
                 particle_datas): #[ParticleData]
        super(PhysicsResourceData, self).__init__(e_resource_id, ERESOURCE_DATA_TYPE.PHYSICS)
        self.particle_datas = particle_datas

class BehaviorResourceData(EntityResourceData):
    def __init__(self,
                 e_resource_id, #int
                 behavior_state_id_lists, #((int,),)
                 initial_behavior_state_ids): #(int,)
        super(BehaviorResourceData, self).__init__(e_resource_id, ERESOURCE_DATA_TYPE.BEHAVIOR)
        self.behavior_state_id_lists = behavior_state_id_lists
        self.initial_behavior_state_ids = initial_behavior_state_ids

class EntityResourceFactory:
    load_sprite_data = None #func* to SpriteImageManager.loadSpriteData()

    def __init__(self):
        pass

    def createResourceDataCollection(self,
                                     e_resource_collection_id):
        file = open(ENTITY_ROOT_PATH + ENTITY_FILENAME_TAG + str(e_resource_collection_id))
        json_dict = json.loads(file.read())
        file.close()

        e_resource_ids = dict() #convert JSON string to ENUM
        for e_resource_data_type_str, e_resource_id in json_dict.items():
            e_resource_data_type = ERESOURCE_DATA_TYPE(int(e_resource_data_type_str))
            e_resource_ids[e_resource_data_type] = e_resource_id

        return EntityDataCollection(e_resource_collection_id = e_resource_collection_id,
                                    e_resource_ids = e_resource_ids)

    def createResourceData(self,
                           e_resource_data_type, #ERESOURCE_DATA_TYPE
                           e_resource_id): #int
        if e_resource_data_type == ERESOURCE_DATA_TYPE.SPRITE:
            return self.createSpriteResourceData(e_resource_id = e_resource_id)
        if e_resource_data_type == ERESOURCE_DATA_TYPE.PHYSICS:
            return self.createPhysicsResourceData(e_resource_id = e_resource_id)
        if e_resource_data_type == ERESOURCE_DATA_TYPE.BEHAVIOR:
            return self.createBehaviorResourceData(e_resource_id = e_resource_id)

    def createSpriteResourceData(self,
                                 e_resource_id): #int
        file = open(ENTITY_ROOT_PATH + ENTITY_SPRITE_PATH + SPRITEDATA_FILENAME_TAG + str(e_resource_id))
        json_dict = json.loads(file.read())
        file.close()
        #We have 1 SpriteInstanceData per subcomponent
        sprite_instance_datas_list = list()
        for spritedataslist in json_dict["spritedataslists"]:
            #we have one entry per sprite instance
            #1 sprite instance can cover multiple behavior states
            #(beacuse not every behavior state need have a unique sprite set)
            sprite_instance_datas = list() #[SpriteInstanceData]
            for spritedata in spritedataslist["spritedatas"]:
                #we will hash all of these ID's to the same sprite instance
                behavior_state_ids = spritedata["behaviorstates"]#[int]
                sprite_data_id = spritedata["spriteid"] #int
                #we use the SpriteImageManager to turn a sprite_id into a full SpriteData for us
                sprite_data = EntityResourceFactory.load_sprite_data(sprite_id = sprite_data_id)
                sprite_instance_datas.append(SpriteInstanceData(behavior_state_ids = behavior_state_ids,
                                                                sprite_data = sprite_data))
            sprite_instance_datas_list.append(tuple(sprite_instance_datas))
        #has all of the data to generate the subcomponents
        #each subcomponent can have multiple sprite instances to cover all states
        return SpriteResourceData(e_resource_id = e_resource_id,
                                  sprite_instance_datas_list =tuple(sprite_instance_datas_list))

    def createPhysicsResourceData(self,
                                  e_resource_id): #int
        file = open(ENTITY_ROOT_PATH + ENTITY_PHYSICS_PATH + PHYSICS_FILENAME_TAG + str(e_resource_id))
        json_dict = json.loads(file.read())
        particle_datas = list()
        for particledata in json_dict["particledatas"]:
            particle_datas.append(ParticleData(inverse_mass = particledata["inversemass"],
                                               damping = particledata["damping"],
                                               offsets = tuple(particledata["offsets"])))

        file.close()
        return PhysicsResourceData(e_resource_id = e_resource_id,
                                   particle_datas = tuple(particle_datas))

    def createBehaviorResourceData(self,
                                   e_resource_id): #int
        file = open(ENTITY_ROOT_PATH + ENTITY_BEHAVIOR_PATH + BEHAVIOR_FILENAME_TAG + str(e_resource_id))
        json_dict = json.loads(file.read())
        behavior_state_id_lists = list()
        initial_states = list() #1 int per subcomponent
        for behaviorfsm in json_dict["behaviorfsms"]:
            behavior_state_id_lists.append(tuple(behaviorfsm["behaviorstateids"]))
            initial_states.append(behaviorfsm["initialstate"])
        file.close()
        return BehaviorResourceData(e_resource_id = e_resource_id,
                                    behavior_state_id_lists = tuple(behavior_state_id_lists),
                                    initial_behavior_state_ids = tuple(initial_states))

# resource_data_collections refers to a single entity, and the list of its resource datas for each component
# resource_datas refer to each component of an entity
# spawnElement creates and entity (with several components)
# loadResourceDataCollection is all the resource datas for an entity (each component)
# loadResourceDatas - the resource_id passed in is for a list of component specific resource_ids
#   go to disk and get each individual resource_id and create a container genereic ResourceData per each
#   that genereic ResourceData will turn into a specific ResourceData when passed to the factory
class EntityResourceManager(ResourceManager):
    create_component_methods = dict() #{ERESOURCE_DATA_TYPE : func* createComponent}
    #ComponentSystem.getSceneComponentPtrs
    get_component_ptr_methods = dict() #{SRESOURCE_DATA_TYPE : func* ComponentSystem.getSceneComponentPtrs}
    call_request_pointers_methods = dict() #{SRESOURCE_DATA_TYPE : func* ComponentSystem.requestPointers}


    def __init__(self): #{func pointers to create_component methods}
        super(EntityResourceManager, self).__init__()

        self._resource_factory = EntityResourceFactory()
        self._entity_data_collections = dict() #{int : ResourceDataCollection}
        self._e_resource_datas = dict() #{int : EResourceData}

    def spawnEntity(self,
                    e_resource_collection_id, #int
                    layer_level_id): #int
        self._loadEntityDataCollection(e_resource_collection_id = e_resource_collection_id)
        new_element_id = self._createEntity(e_resource_collection_id = e_resource_collection_id,
                                            layer_level_id= layer_level_id)
        return new_element_id

    def _loadEntityDataCollection(self,
                                  e_resource_collection_id): #int
        if self._entity_data_collections.get(e_resource_collection_id) is None:
            entity_data_collection = self._resource_factory.createResourceDataCollection(e_resource_collection_id)
            self._entity_data_collections[e_resource_collection_id] = entity_data_collection
            for e_resource_data_type, e_resource_id in entity_data_collection.e_resource_ids.items():
                self._loadEntityResourceData(e_resource_data_type = e_resource_data_type,
                                             e_resource_id = e_resource_id)

    def _loadEntityResourceData(self,
                                e_resource_data_type, #ERESOURCE_DATA_TYPE
                                e_resource_id): #int
        if self._e_resource_datas.get(e_resource_id) is None:
            e_resource_data = self._resource_factory.createResourceData(e_resource_data_type = e_resource_data_type,
                                                                        e_resource_id = e_resource_id)
            self._e_resource_datas[e_resource_id] = e_resource_data

    #Creates the entity by sending data to ComponentSystems
    #Gets the components from the ComponentSystems to add the the SceneLayer
    #The ComponentSystems will only return relevent scene componets
    def _createEntity(self,
                      e_resource_collection_id,
                      layer_level_id): #int
        component_element_id = self.createElementId()
        e_resource_collection = self._entity_data_collections[e_resource_collection_id]

        #call the component systems createComponent method on the data
        for e_resource_data_type, e_resource_id in e_resource_collection.e_resource_ids.items():
            e_resource_data = self._e_resource_datas[e_resource_id]
            EntityResourceManager.create_component_methods[e_resource_data_type] \
                (component_element_id = component_element_id,
                 layer_level_id = layer_level_id,
                 resource_data = e_resource_data)

        #get any component or subcomponent from the componentSystems that needs to be added to the scene layer
        for e_resource_data_type in EntityResourceManager.get_component_ptr_methods.keys():
            entity_component_ptrs = EntityResourceManager.get_component_ptr_methods[e_resource_data_type]\
                (component_element_id = component_element_id)
            for entity_component_ptr in entity_component_ptrs:
                ResourceManager.add_component_to_layer(layer_level_id = layer_level_id,
                                                       scene_component = entity_component_ptr)
        #update the component pointers
        #After all portions of the entity are created, we can pass the needed function ptrs (etc) around
        for e_resource_data_type in EntityResourceManager.call_request_pointers_methods.keys():
            EntityResourceManager.call_request_pointers_methods[e_resource_data_type](component_element_id = component_element_id)

        return component_element_id