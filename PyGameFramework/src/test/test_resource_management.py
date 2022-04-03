import unittest
import resource_management
from resource_management import ERESOURCE_DATA_TYPE
import pygame

class TestSpriteImageManager(unittest.TestCase):

    def setUp(self): #called before each test
        self.sprite_image_manager = resource_management.SpriteImageManager()

    def tearDown(self): #called after each test
        pass

    @classmethod
    def setUpClass(cls): #called once at beginning of test case
        pygame.init() #needed for the pygame.image.load function
        pygame.display.set_mode((1,1), 0)

        #this is actually the same, but since we are in the "test" folder we will get test resources
        resource_management.ENTITY_ROOT_PATH = \
            'resource\\entity\\'

        #this does not exist in the src folder
        resource_management.IMAGE_ROOT_PATH = \
            'assets\\'

    @classmethod
    def tearDownClass(cls): #called once at end of test case
        pass

    def test_loadSpriteData(self):
        SPRITE_ID_1 = 4000000 #Test file resource
        SPRITE_ID_2 = 4000002 #Test file resource
        #we will be using this shortcut to verify sprite_data functions
        sprite_datas = self.sprite_image_manager._sprite_datas
        #List is empty when loaded
        self.assertEqual(len(sprite_datas), 0)

        #load a valid spritedata
        self.sprite_image_manager.loadSpriteData(sprite_id = SPRITE_ID_1)
        self.assertEqual(len(sprite_datas), 1)

        #don't load duplicates, and should not create new object
        sprite_data_object_id1 = id(sprite_datas[SPRITE_ID_1])
        self.sprite_image_manager.loadSpriteData(sprite_id = SPRITE_ID_1)
        self.assertEqual(len(sprite_datas), 1)
        self.assertEqual(sprite_data_object_id1, id(sprite_datas[SPRITE_ID_1])) #no change

        #load a new resource and it has a uniqe id
        self.sprite_image_manager.loadSpriteData(sprite_id=SPRITE_ID_2)
        self.assertEqual(len(sprite_datas), 2)
        sprite_data_object_id2 = id(sprite_datas[SPRITE_ID_2])
        self.assertEqual(sprite_data_object_id1, id(sprite_datas[SPRITE_ID_1])) #no change to original
        self.assertNotEqual(sprite_data_object_id1, sprite_data_object_id2) #new one is unique

    def test_loadSpriteImage(self):
        IMAGE_ID1 = 2000000
        IMAGE_ID2 = 2000001
        IMAGE_EXT = "png"
        #we will be using this shortcut to verify sprite_data functions
        sprite_images = self.sprite_image_manager._sprite_images
        #List is empty when loaded
        self.assertEqual(len(sprite_images), 0)

        #load a valid spritedata
        self.sprite_image_manager.loadSpriteImage(image_id = IMAGE_ID1,
                                                  file_type = IMAGE_EXT)
        self.assertEqual(len(sprite_images), 1)

        #don't load duplicates, and should not create new object
        sprite_image_object_id1 = id(sprite_images[IMAGE_ID1])
        self.sprite_image_manager.loadSpriteImage(image_id = IMAGE_ID1,
                                                  file_type = IMAGE_EXT)
        self.assertEqual(len(sprite_images), 1)
        self.assertEqual(sprite_image_object_id1, id(sprite_images[IMAGE_ID1])) #no change

        #load a new resource and it has a uniqe id
        self.sprite_image_manager.loadSpriteImage(image_id = IMAGE_ID2,
                                                  file_type = IMAGE_EXT)
        self.assertEqual(len(sprite_images), 2)
        sprite_image_object_id2 = id(sprite_images[IMAGE_ID2])
        self.assertEqual(sprite_image_object_id1, id(sprite_images[IMAGE_ID1])) #no change to original
        self.assertNotEqual(sprite_image_object_id1, sprite_image_object_id2) #new one is unique

    def test_loadPanoramaImage(self):
        pass

    def test_applySpriteAccessories(self):
        #Mock object and function for Render.CombineSurface
        class DummyImage:
            def __init__(self):
                pass
        def combine_image(image_source, image_dest, coodinates):
            return DummyImage()
        self.sprite_image_manager._combine_image = combine_image

        SPRITE_ID_1 = 4000000
        SPRITE_ID_2 = 4000001
        SPRITE_ID_3 = 4000002

        IMAGE_ID1 = 2000000 #we know that this is the ID that SPRITE_DATA1 provides
        IMAGE_ID2 = 2000001
        IMAGE_ID3 = 2000002
        IMAGE_ID4 = 2000003
        IMAGE_ID5 = 2000004
        IMAGE_ID6 = 2000005

        #shortcut for the data structs we will test
        sprite_images = self.sprite_image_manager._sprite_images
        sprite_datas = self.sprite_image_manager._sprite_datas

        #they start empty
        self.assertEqual(len(sprite_images), 0)
        self.assertEqual(len(sprite_datas), 0)

        self.sprite_image_manager.loadSpriteData(sprite_id = SPRITE_ID_1)
        #added 1 to each
        self.assertEqual(len(sprite_images), 1)
        self.assertEqual(len(sprite_datas), 1)

        sprite_data_objID1 = id(sprite_datas[SPRITE_ID_1])
        sprite_image_objID1 = id(sprite_images[IMAGE_ID1])

        #we know that the only spriteData is linked to the only image
        self.assertEqual(sprite_image_objID1, id(sprite_datas[SPRITE_ID_1].image))

        ###CALL 1###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_1,
                                                         sprite_image_ids = (IMAGE_ID1,),
                                                         accessory_image_ids = (IMAGE_ID2,))
        #We should have added 2 more images - a new single image and a combined image
        self.assertEqual(len(sprite_images), 3)
        self.assertEqual(sprite_image_objID1, id(sprite_images[IMAGE_ID1])) #this should not have changed
        self.assertEqual(sprite_data_objID1, id(sprite_datas[SPRITE_ID_1])) #this should not have changed
        self.assertNotEqual(sprite_image_objID1, id(sprite_datas[SPRITE_ID_1].image)) #should have new image
        new_image = sprite_images[(IMAGE_ID1, IMAGE_ID2)] #we created this new image key
        self.assertNotEqual(new_image, None)
        sprite_image_objID1 = id(sprite_datas[SPRITE_ID_1].image) #update the ID

        ###CALL 2###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_1,
                                                         sprite_image_ids = (IMAGE_ID1,),
                                                         accessory_image_ids = (IMAGE_ID3,))
        #We should have added 2 more images - a new single image and a combined image
        self.assertEqual(len(sprite_images), 5)
        new_image = sprite_images[(IMAGE_ID1, IMAGE_ID3)]  # we created this new image key
        self.assertNotEqual(new_image, None)
        self.assertNotEqual(sprite_image_objID1, id(sprite_datas[SPRITE_ID_1].image))  # should have new image
        sprite_image_objID1 = id(sprite_datas[SPRITE_ID_1].image) #update the ID

        ###CALL 3###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_1,
                                                         sprite_image_ids = (IMAGE_ID1,),
                                                         accessory_image_ids = (IMAGE_ID2,IMAGE_ID3,))
        #Since each individual image exists already, we should only add 1 new one for the combo
        self.assertEqual(len(sprite_images), 6)
        new_image = sprite_images[(IMAGE_ID1, IMAGE_ID2, IMAGE_ID3)]  # we created this new image key
        self.assertNotEqual(new_image, None)
        self.assertNotEqual(sprite_image_objID1, id(sprite_datas[SPRITE_ID_1].image))  # should have new image
        sprite_image_objID1 = id(sprite_datas[SPRITE_ID_1].image) #update the ID

        ###CALL 4###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_1,
                                                         sprite_image_ids = (IMAGE_ID1,IMAGE_ID2),
                                                         accessory_image_ids = (IMAGE_ID3,))
        #we already have this key, so we should not add a new image
        self.assertEqual(len(sprite_images), 6)
        self.assertEqual(sprite_image_objID1, id(sprite_datas[SPRITE_ID_1].image))  # should not have changed

        ###CALL 5###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_2,
                                                         sprite_image_ids = (IMAGE_ID1,),
                                                         accessory_image_ids = (IMAGE_ID2,IMAGE_ID3))
        self.assertEqual(len(sprite_datas), 2) #added a new sprite data
        self.assertEqual(len(sprite_images), 6) #no change, we had all of those already
        self.assertNotEqual(id(sprite_datas[SPRITE_ID_1]), id(sprite_datas[SPRITE_ID_2]))  #unique instances
        self.assertEqual(id(sprite_datas[SPRITE_ID_1].image), id(sprite_datas[SPRITE_ID_2].image))  #shared image
        sprite_image_objID1 = id(sprite_datas[SPRITE_ID_1].image)  # update the ID

        ###CALL 6###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_3,
                                                         sprite_image_ids = (IMAGE_ID3,),
                                                         accessory_image_ids = (IMAGE_ID4, IMAGE_ID5, IMAGE_ID6))
        self.assertEqual(len(sprite_datas), 3) #added a new sprite data
        self.assertEqual(len(sprite_images), 10) #3 new individual images, and 1 new combination
        self.assertEqual(sprite_image_objID1, id(sprite_datas[SPRITE_ID_2].image))  #no change to this image
        sprite_image_objID3 = id(sprite_datas[SPRITE_ID_3].image)  # update the ID

        ###CALL 7###
        self.sprite_image_manager.applySpriteAccessories(sprite_id = SPRITE_ID_3,
                                                         sprite_image_ids = (IMAGE_ID3,),
                                                         accessory_image_ids = (IMAGE_ID4, IMAGE_ID6, IMAGE_ID5))
        self.assertEqual(len(sprite_datas), 3) #added a new sprite data
        self.assertEqual(len(sprite_images), 11) #order matters, added a new image
        self.assertNotEqual(sprite_image_objID3, id(sprite_datas[SPRITE_ID_3].image))  #new image


class TestEResourceManager(unittest.TestCase):
    def setUp(self): #called before each test
        # dummy methods
        def createSpriteComponent(component_id, resource_data):
            pass
        def createBehaviorComponent(component_id, resource_data):
            pass
        def createPhysicsComponent(component_id, resource_data):
            pass
        create_component_methods = {ERESOURCE_DATA_TYPE.BEHAVIOR : createBehaviorComponent,
                                    ERESOURCE_DATA_TYPE.PHYSICS: createPhysicsComponent,
                                    ERESOURCE_DATA_TYPE.SPRITE: createSpriteComponent}
        self.sprite_manager = resource_management.SpriteImageManager()
        self.eresource_manager = resource_management.EResourceManager(create_component_methods = create_component_methods,
                                                                      load_sprite_data = self.sprite_manager.loadSpriteData)
    def tearDown(self): #called after each test
        pass

    @classmethod
    def setUpClass(cls): #called once at beginning of test case
        pygame.init() #needed for the pygame.image.load function
        pygame.display.set_mode((1,1), 0)

        #this is actually the same, but since we are in the "test" folder we will get test resources
        resource_management.ENTITY_ROOT_PATH = \
            'resource\\entity\\'

        #this does not exist in the src folder
        resource_management.IMAGE_ROOT_PATH = \
            'assets\\'

    def test_createRemoveEntityId(self):
        #shortcut
        entity_ids = self.eresource_manager._entity_ids
        self.assertEqual(len(entity_ids), 0)

        ###CALL 1###
        entity_id = self.eresource_manager.createEntityId()
        self.assertEqual(len(entity_ids), 1)
        self.assertEqual(entity_id, 0)
        self.assertEqual(entity_ids[0], True)
        self.assertEqual(self.eresource_manager._next_entity_id, 1)

        ###CALL 2###
        entity_id = self.eresource_manager.createEntityId()
        self.assertEqual(len(entity_ids), 2)
        self.assertEqual(entity_id, 1)
        self.assertEqual(entity_ids[0], True)
        self.assertEqual(entity_ids[1], True)
        self.assertEqual(self.eresource_manager._next_entity_id, 2)

        ###CALL 3###
        self.eresource_manager.removeEntityId(0)
        self.assertEqual(len(entity_ids), 2)
        self.assertEqual(self.eresource_manager._next_entity_id, 2)
        self.assertEqual(entity_ids[0], False)
        self.assertEqual(entity_ids[1], True)

        ###CALL 4###
        self.eresource_manager.removeEntityId(0)
        self.assertEqual(len(entity_ids), 2)
        self.assertEqual(self.eresource_manager._next_entity_id, 2)
        self.assertEqual(entity_ids[0], False)
        self.assertEqual(entity_ids[1], True)

        ###CALL 5###
        self.eresource_manager.removeEntityId(1)
        self.assertEqual(len(entity_ids), 2)
        self.assertEqual(self.eresource_manager._next_entity_id, 2)
        self.assertEqual(entity_ids[0], False)
        self.assertEqual(entity_ids[1], False)

        ###CALL 6###
        entity_id = self.eresource_manager.createEntityId()
        self.assertEqual(entity_id, 2)
        self.assertEqual(len(entity_ids), 3)
        self.assertEqual(self.eresource_manager._next_entity_id, 3)
        self.assertEqual(entity_ids[0], False)
        self.assertEqual(entity_ids[1], False)
        self.assertEqual(entity_ids[2], True)

    #Tests collections and individual resource_datas
    def test_loadEResourceData(self):
        E_RESOURCE_ID0 = 0
        E_RESOURCE_ID1 = 1
        E_RESOURCE_ID2 = 2
        E_RESOURCE_ID3 = 3
        BEH_RESOURCE_ID0 = 1000000
        BEH_RESOURCE_ID2 = 1000002
        PHY_RESOURCE_ID0 = 2000000
        PHY_RESOURCE_ID2 = 2000002
        SPR_RESOURCE_ID0 = 3000000

        collections = self.eresource_manager._e_resource_data_collections
        resource_datas = self.eresource_manager._e_resource_datas
        self.assertEqual(len(collections), 0)
        self.assertEqual(len(resource_datas), 0)

        ###CALL 1###
        self.eresource_manager.loadEResourceDataCollection(e_resource_id = E_RESOURCE_ID0)
        self.assertEqual(len(collections), 1)
        self.assertEqual(len(resource_datas), 3)
        collection0_objID = id(collections[E_RESOURCE_ID0])
        beh_resource0_objID = id(resource_datas[BEH_RESOURCE_ID0])
        phy_resource0_objID = id(resource_datas[PHY_RESOURCE_ID0])
        sprt_resource0_objID = id(resource_datas[SPR_RESOURCE_ID0])

        ###CALL 2###
        self.eresource_manager.loadEResourceDataCollection(e_resource_id = E_RESOURCE_ID0)
        self.assertEqual(len(collections), 1) #no changes to anything
        self.assertEqual(len(resource_datas), 3)
        self.assertEqual(collection0_objID, id(collections[E_RESOURCE_ID0]))
        self.assertEqual(beh_resource0_objID, id(resource_datas[BEH_RESOURCE_ID0]))
        self.assertEqual(phy_resource0_objID, id(resource_datas[PHY_RESOURCE_ID0]))
        self.assertEqual(sprt_resource0_objID, id(resource_datas[SPR_RESOURCE_ID0]))

        ###CALL 3###
        self.eresource_manager.loadEResourceDataCollection(e_resource_id = E_RESOURCE_ID1)
        self.assertEqual(len(collections), 2) #added a new collection
        self.assertEqual(len(resource_datas), 3) #but none of the resource datas were unique, no change here

        ###CALL 4###
        self.eresource_manager.loadEResourceDataCollection(e_resource_id = E_RESOURCE_ID2)
        self.assertEqual(len(collections), 3) #added a new collection
        self.assertEqual(len(resource_datas), 5) #2 new resource datas
        self.assertEqual(collection0_objID, id(collections[E_RESOURCE_ID0]))
        beh_resource2_objID = id(resource_datas[BEH_RESOURCE_ID2])
        phy_resource2_objID = id(resource_datas[PHY_RESOURCE_ID2])

        ###CALL 5###
        self.eresource_manager.loadEResourceDataCollection(e_resource_id = E_RESOURCE_ID3)
        self.assertEqual(len(collections), 4) #added a new collection
        self.assertEqual(len(resource_datas), 6) #1 new resource datas
        self.assertEqual(beh_resource2_objID, id(resource_datas[BEH_RESOURCE_ID2])) #no change
        self.assertEqual(phy_resource2_objID, id(resource_datas[PHY_RESOURCE_ID2]))

    def test_createEntityComponenets(self):
        pass #called in spawn entity

    def test_spawnEntity(self):
        E_RESOURCE_ID0 = 0
        E_RESOURCE_ID3 = 3

        entity_ids = self.eresource_manager._entity_ids
        collections = self.eresource_manager._e_resource_data_collections
        self.assertEqual(len(entity_ids), 0)
        self.assertEqual(len(collections), 0)

        ###CALL 1###
        self.eresource_manager.spawnEntity(e_resource_id = E_RESOURCE_ID0)
        self.assertEqual(len(entity_ids), 1)
        self.assertEqual(len(collections), 1)

        ###CALL 2###
        self.eresource_manager.spawnEntity(e_resource_id = E_RESOURCE_ID0)
        self.assertEqual(len(entity_ids), 2) #new entity created
        self.assertEqual(len(collections), 1) #no change - already loaded

        ###CALL 3###
        self.eresource_manager.spawnEntity(e_resource_id = E_RESOURCE_ID3)
        self.assertEqual(len(entity_ids), 3)  # new entity created
        self.assertEqual(len(collections), 2)  # new collection