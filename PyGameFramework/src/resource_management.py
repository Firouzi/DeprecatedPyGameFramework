import json
import pygame

#resource data filepaths
ENTITY_ROOT_PATH = 'resource\\entity\\'
ENTITY_BEHAVIOR_PATH = 'behavior\\'
ENTITY_PHYSICS_PATH = 'physics\\'
ENTITY_SPRITE_PATH = 'sprite\\'
IMAGE_ROOT_PATH = 'F:\\Dropbox\\Projects\\PyGame_Framework\\assets\\'
SPRITE_IMAGE_PATH = 'sprite\\'
PANORAMA_IMAGE_PATH = 'panorama\\'
ATLAS_IMAGE_PATH = 'tilemap\\'
SPRITEIMAGE_FILENAME_TAG = 'spriteimage_'


"""
ResourceManager parent class is inhereted to manage the different resources
This parent class really only handles assigning the dynamic ID's and tags.

Their is a naming convention used for the different types of data in the engine.

ID's
-"resource"_id's refer to the ID for data on disk.  Using the resource_id tells you 
the filename to load.  Examples include "s_resource_id" and "e_resource_id"

"element"_id's refer to dynamic components in game.  When a component is created by
the ResourceManager classes, it is assigned a unique ID number.

"tag"_id's refer to a chosen tag value assigned to an component.  To assign a tag,
you choose the element_id which will be "tagged".  The reason for doing this is that
the element_id's are dynamically created, and thus not known beforehand.  For any kind
of scripted event, you may want to reference a specific game component.  You can then
set the tag of that component when it is created, and find it later by the assigned tag.

"layer_level_id" is assigned to each scenelayer and is predetermined in the resource_data on disk.
The layer_level determines the order that renderable_layers are rendered.  Lowest value is rendered.
Only one layer can be loaded for a given layer_level_id.  New components are added to the layer specified
by layer_level_id.  SceneLayers are not given element_id's.

ResourceData
The ResourceData and it's children is a data container class that is loaded by a resource_id.
It is used to spawn new components.  Once loaded from disk, it is stored by the resource_id and thus
is not reloaded again from disk.  You can create multiple instances of a Component from the same
ResourceData

ResourceDataCollection and it's children contains a resource_id for it's collection, and then a
set of resource_id's mapping to ResourceDatas.  When loaded, will load all the mapped ResourceDatas
as well, but then collections of Components instances can be created without going back to disk.

ResourceManager static functions
several static functions are defined in ResourceManager and it's children, which are used to
create the actual components.  ResourceManager only is responsible for loading from disk and
storing those loaded data files.  The ComponentSystems have the functions which dynamically create
the Components.

ResourceManager sequence
a ResourceManager provides "spawn" methods, which accept a resource_id.  From here, they will first
load the resources, then use the callback functions (from the ComponentSystems) to create a new instance
They will return the newly created element_id(s).  

"""

#Generic data for a single component of any type
class ResourceData:
    def __init__(self):
        pass

#Parent type for the Scene and Entity resource managers
#Tracks all loaded resourceDatas and ResourceCollections, as well as tags.
#Uses factory to load and create ResourceDatas and factory methods to create components
class ResourceManager:
    #SceneHandler.addSceneComponent
    add_component_to_layer = None

    def __init__(self): #{func pointers to create_component methods}
        #element generic term for either entity or scene (element_id = scene_id OR entity_id)
        self._element_ids = dict()  # {int : bool}
        #keys on tag id of an element, and matches with the active element_id
        #The purpose of the tags is to be able to dynamically access an active element with
        #pre-programmed game events.  An Eement_id is essentially random/uknwown, and a resource_id can be
        #used by multiple elements.  Tags are generally assigned when spawned and must be designated and
        #known as part of the game design.  A way of finding that element when active
        self._element_tag_ids = dict() #{int: int}
        self._next_element_id = 0

    #THERE CAN ONLY BE ONE
    #If this e_tag_id is already in use, the tag will be switched to the passed in entity_id
    #asserts an error if the entity_id does not exist
    #returns False if the tag_id in use already by an active entity
    #returns False if the passed in entity_id is inactive
    #returns True if the entity exists, is active, and tag is unique
    def setTagId(self,
                 element_id, #int
                 tag_id): #int
        assert(self._element_ids.get(element_id) is not None), \
            "Element tag " + str(tag_id) + " assigned to non-existant element_id: " + str(element_id)
        retVal = self._element_ids.get(element_id) #will be False if element is inactive
        current_tagged_element = self._element_tag_ids.get(tag_id)
        if current_tagged_element is not None: #we have used this tag already
            if self._element_ids.get(current_tagged_element):
                retVal = False #signify there may be an issue, reassigning a tag from an active element
        self._element_tag_ids[tag_id] = element_id #finally, assign (or reassign) the tag
        return retVal

    #returns the entity_id referenced by the tag id
    #returns None if that tag is not in the dict
    #returns False if that entity is not active
    def getElementIdFromTagId(self,
                             tag_id):
        element_id = self._element_tag_ids.get(tag_id)
        if element_id is not None: #it has been created before now
            if self._element_ids.get(element_id): #it is active
                return element_id
            else: #Was created, but is inactive
                return False
        return None #Go Fish

    #generate a unique entity_id dynamically
    def createElementId(self):
        self._element_ids[self._next_element_id] = True
        self._next_element_id += 1
        return self._next_element_id - 1

    def removeElementId(self,
                        element_id): #int
        if self._element_ids.get(element_id) is not None:
            self._element_ids[element_id] = False

class SpriteData:
    def __init__(self,
                 sprite_id,  # int
                 image,  # pygame.image
                 file_type,  # string
                 is_eightway,  # bool
                 num_frames,  # int
                 frame_times_ms, #(int,)
                 frames):  # [int]
        self.sprite_id = sprite_id
        self.image = image
        self.file_type = file_type
        self.is_eightway = is_eightway
        self.num_frames = num_frames
        self.frame_times_ms = frame_times_ms
        self.frames = frames

        self.references = 0  # int
        self.protected = False  # bool

    def setImage(self,
                 image):  # pygame.surface
        self.image = image

    def referenced(self):
        self.references += 1

    def unreferenced(self):
        self.references -= 1

#Loads and tracks images and sprite datas
class SpriteImageManager:
    def __init__(self):
        self._sprite_images = dict() #{[int] : pygame.image} - image_id's are the key (base plus accessories)
        self._panorama_images = dict() #{int : pygame.imgage} - image_id's are the key
        self._atlas_images = dict() #{int : pygame.imgage} - image_id's are the key
        self._sprite_datas = dict() #{int : SpriteData} - sprite_id is the key
        self._combine_image = None #pointer to render.combineSurface() function

    def loadSpriteData(self,
                       sprite_id): #int
        if self._sprite_datas.get(sprite_id) is None:
            file = open(ENTITY_ROOT_PATH + ENTITY_SPRITE_PATH + SPRITEIMAGE_FILENAME_TAG + str(sprite_id))
            json_dict = json.loads(file.read())
            file.close()
            self._sprite_datas[sprite_id] = SpriteData(sprite_id = sprite_id,
                                                       image = self.loadSpriteImage(image_id = json_dict["imageid"],
                                                                                    file_type = json_dict["filetype"]),
                                                       file_type = json_dict["filetype"],
                                                       is_eightway = json_dict["iseightway"],
                                                       num_frames = json_dict["numframes"],
                                                       frame_times_ms = tuple(json_dict["frametimesms"]),
                                                       frames = json_dict["frames"])
        return self._sprite_datas[sprite_id]

    def loadSpriteImage(self,
                        image_id, #int
                        file_type): #string
        if self._sprite_images.get(image_id) is None:
            filepath = IMAGE_ROOT_PATH + SPRITE_IMAGE_PATH + str(image_id) + "." + file_type
            self._sprite_images[image_id] = pygame.image.load(filepath).convert_alpha()
        return self._sprite_images[image_id]

    def loadPanoramaImage(self,
                          image_id, #int
                          file_type): #string
        if self._panorama_images.get(image_id) is None:
            filepath = IMAGE_ROOT_PATH + PANORAMA_IMAGE_PATH + str(image_id) + "." + file_type
            self._panorama_images[image_id] = pygame.image.load(filepath).convert_alpha()
        return self._panorama_images[image_id]

    def loadAtlasImage(self,
                       image_id, #int
                       file_type): #string
        if self._atlas_images.get(image_id) is None:
            filepath = IMAGE_ROOT_PATH + ATLAS_IMAGE_PATH + str(image_id) + "." + file_type
            self._atlas_images[image_id] = pygame.image.load(filepath).convert_alpha()
        return self._atlas_images[image_id]

    #This method will handle loading any unloaded raw iamges, and combine them into 1 new sprite
    #Can be used to add an accessory to an existing sprite, or to load a sprite in several layers at once
    def applySpriteAccessories(self,
                               sprite_id, #the ID for the sprite_data which will use this image
                               sprite_image_ids, #(int) - index 0 is the base sprite, the rest are the accessories
                               accessory_image_ids): #(int) - list of accessories to apply to the sprite image in order

        #If the SpriteData isn't loaded from disk, load it now
        if self._sprite_datas.get(sprite_id) is None:
            self.loadSpriteData(sprite_id)

        #We won't be able to layer images with different file types :(
        file_type = self._sprite_datas[sprite_id].file_type

        #load each of the individual images as necessary
        for sprite_image_id in sprite_image_ids:
            if self._sprite_images.get(sprite_image_id) is None:
                self._sprite_images[sprite_image_id] = self.loadSpriteImage(image_id = sprite_image_id,
                                                                            file_type = file_type)

        #If this base_sprite combination doesn't exist yet, we need to build it first
        if len(sprite_image_ids) > 1 and self._sprite_images.get(sprite_image_ids) is None:
            new_image = self._sprite_images.get(sprite_image_ids[0]) #start with the base image
            numb_layers = len(sprite_image_ids) #total number of images for this sprite combo
            layer_count = 1
            #Start with the new_image (index 0) and apply each of the rest of the images on top
            while layer_count < numb_layers:
                new_image = self._combine_image(new_image,
                                                 self._sprite_images[sprite_image_ids[layer_count]],
                                                 [0,0,0,0]) #coordinates
                layer_count +=1
            self._sprite_images[sprite_image_ids] = new_image #add to dict with the list as the key
        new_image_key = list(sprite_image_ids)
        #now load all of the accessory images as necessary, also builds the new key for the image

        for accessory_image_id in accessory_image_ids:
            if self._sprite_images.get(accessory_image_id) is None:
                self._sprite_images[accessory_image_id] = self.loadSpriteImage(image_id = accessory_image_id,
                                                                               file_type = file_type)
            new_image_key.append(accessory_image_id)

        #layer the newly loaded accessory images on top of the sprite image
        if self._sprite_images.get(tuple(new_image_key)) is None:
            new_image = self._sprite_images.get(sprite_image_ids)
            for accessory_image_id in accessory_image_ids:
                new_image = self._combine_image(new_image,
                                                 self._sprite_images[accessory_image_id],
                                                 [0,0,0,0]) #coordinates
            self._sprite_images[tuple(new_image_key)] = new_image

        #apply the new image to the SpriteData
        self._sprite_datas[sprite_id].setImage(image = self._sprite_images[tuple(new_image_key)])
