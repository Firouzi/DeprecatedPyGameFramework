from enum import Enum
from resource_management import ResourceManager, ResourceData
import json
import xml.sax

#resource data filepaths
SCENE_ROOT_PATH = 'resource\\scene\\'
LAYER_ROOT_PATH = 'layer\\'
SCENE_PANORAMA_PATH = 'panorama\\'
SCENE_ATLAS_PATH = ""

TILED_XML_EXTENSION = ".tmx"
TILED_JSON_EXTENSION = ".json"

class SCENE_LAYER_TYPE(Enum):
    NA = 0
    RENDERABLE = 1
    PHYSICAL = 2
    ENVIRONMENT = 3
    EVENT = 4

class RENDERABLE_LAYER_TYPE(Enum):
    NA = 0
    ATLAS = 1 #uses a tilemap
    IMAGE = 2 #all sprites
    MIXED = 3 #combo of tiles and sprites
    PANORAMA = 4

class TILE_PERSPECTIVE(Enum):
    NA = 0
    SIDE = 1
    TOPDOWN = 2
    DIMETRIC = 3

class SRESOURCE_DATA_TYPE(Enum):
    UNKNOWN = 0
    TILEMAP = 1
    PANORAMA = 2
    ATLAS = 3
    ENVIRONMENT = 4
    BARRIER = 5
    EVENT = 6


def stringListToIntList(list):
    index = 0
    for string in list:
        list[index] = int(string)
        index+=1
    return list

#called within the TiledXmlHandler to parse the atlas xml data
#DEPRECATED - SWITCHED TO JSON LOADER
class AtlasXmlHandler(xml.sax.ContentHandler):
    load_atlas_image = None

    def __init__(self,
                 gamescene_resource_id, #int
                 atlas_index, #int
                 first_gid): #int
        super(AtlasXmlHandler, self).__init__()
        self.animated_tile_resource_data = dict() #{int : AnimatedTileResourceData} - keyed on gid of first tile
        self.floating_tile_gids = dict() #{int : bool}
        self.atlas_resource_data = AtlasResourceData(gamescene_resource_id = gamescene_resource_id,
                                                     s_resource_data_type = SRESOURCE_DATA_TYPE.ATLAS,
                                                     atlas_index = atlas_index,
                                                     first_gid = first_gid,
                                                     tile_size_px = [0,0],
                                                     tile_count = 0,
                                                     numb_columns = 0,
                                                     floating_tile_gids = self.floating_tile_gids,
                                                     image_id = 0,
                                                     image = None,
                                                     file_type = "",
                                                     animated_tile_resource_datas = self.animated_tile_resource_data)

        self.current_tag = ""
        self.current_animated_tile_resource_data = None #used to build the animation data structures
        self.current_animated_tile_index = -1
        self.current_tile_ids = list() #keeps a list of frames of tile ids for a single animated tile
        self.current_durations = list() #keeps a list of durations for each tile id (the indexes are relative to each other)

        #a tile may have animation data, or a flag as a floating tile
        self._current_tile_id = -1 #for xml parsing, tracks the tile_id currently being parser

    def startElement(self, tag, attributes):
        self.current_tag = tag

        if self.current_tag == "tileset":
            tile_width = int(attributes["tilewidth"])
            tile_height = int(attributes["tileheight"])
            tile_count = int(attributes["tilecount"])
            numb_columns = int(attributes["columns"])
            self.atlas_resource_data.tile_size_px = (tile_width, tile_height)
            self.atlas_resource_data.tile_count = tile_count
            self.atlas_resource_data.numb_columns = numb_columns

        elif self.current_tag == "image":
            image_path = attributes["source"] #eg "<path>\\#######.png" - we want the integer value of #####, and the filetype
            image_id = int(image_path.split('/')[-1].split(".")[0])
            file_type = image_path.split('/')[-1].split(".")[1]
            image = AtlasXmlHandler.load_atlas_image(image_id = image_id,
                                                     file_type = file_type)
            self.atlas_resource_data.image_id = image_id
            self.atlas_resource_data.file_type = file_type
            self.atlas_resource_data.image = image


        elif self.current_tag == "tile":
            self._current_tile_id = int(attributes["id"])
           # self.current_animated_tile_index = int(attributes["id"])
           # #we setup the resource_data but need to add all of the elements to each of the lists (done in "frame")
           # self.current_animated_tile_resource_data = AnimatedTileResourceData(tile_gids=self.current_tile_ids,  #empty right now
           #                                                                     durations=self.current_durations) #empty right now

        elif self.current_tag == "animation":
            self.current_animated_tile_index = self._current_tile_id
            #we setup the resource_data but need to add all of the elements to each of the lists (done in "frame")
            self.current_animated_tile_resource_data = AnimatedTileResourceData(tile_gids=self.current_tile_ids,  #empty right now
                                                                                durations=self.current_durations) #empty right now

        elif self.current_tag == "frame":
            self.current_tile_ids.append(int(attributes["tileid"]))
            self.current_durations.append(int(attributes["duration"]))

        elif self.current_tag == "property" and self._current_tile_id != -1:
            if attributes["name"] == "floating_tile" and attributes["value"] == "true":
                self.floating_tile_gids[self._current_tile_id] = True



    def endElement(self, tag):
        if tag == "tile":
            #Adding the completed animated tile data to the ResourceData indexed by it's tile id
            if self.current_animated_tile_index != -1:
                self.atlas_resource_data.animated_tile_resource_datas[self.current_animated_tile_index] = \
                    self.current_animated_tile_resource_data
            #reset the data
            self.current_animated_tile_resource_data = None
            self.current_animated_tile_index = -1
            self.current_tile_ids = list()
            self.current_durations = list()
            self._current_tile_id = -1

    def characters(self, content):
        pass #We don't need any data outside of the properties

    def getAtlasResourceData(self):
        return self.atlas_resource_data

#Class that can read the tmx files generated by the Tiled software
#generates the colleciton of resource_datas
#DEPRECATED - SWITCHED TO JSON LOADER
class TiledXmlHandler(xml.sax.ContentHandler):
    #func ptr for the SpriteImageManager load image method
    load_panorama_image = None

    def __init__(self,
                 gamescene_resource_id):
        super(TiledXmlHandler, self).__init__()
        self.gamescene_resource_id = gamescene_resource_id
        #store each atlas resource data by index
        self.atlas_resource_datas = list()
        self.atlas_count = 0
        #store each layer created by layer_level_id
        self.layer_resource_datas = dict()
        #The layers will be built and added as the parser runs
        self.layer_data_collection = LayerDataCollection(gamescene_resource_id = gamescene_resource_id,
                                                         atlas_resource_datas = self.atlas_resource_datas,
                                                         layer_resource_datas = self.layer_resource_datas)

        #properties
        self._tile_size_px = [0,0]

        #Keep track of what is being parsed
        self.current_tag = ""
        self.current_layer_type = ""
        self.current_innerlayer_type = ""
        self.current_object_type = ""

        # for some layers, we need several properties before we create it
        self.current_scene_layer_type = SCENE_LAYER_TYPE.NA
        self.current_renderable_layer_type = RENDERABLE_LAYER_TYPE.NA
        self.current_tile_perspective = TILE_PERSPECTIVE.NA
        self.current_is_needs_sorting = False

        #For building the resources
        self.current_layer_level = 0
        self.current_layer_resource_data = None
        self.current_scene_resource_data = None

        #for tilemaps
        self.current_tiles = None #will be a 2d array of gid's

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.current_tag = tag

        if self.current_tag == "map":
            self.current_layer_type = "map"
            self.layer_data_collection.scene_size_tile = (int(attributes["width"]), int(attributes["height"]))
            self._tile_size_px = (int(attributes["tilewidth"]), int(attributes["tileheight"]))
            layer_width_px = self._tile_size_px[0] * self.layer_data_collection.scene_size_tile[0]
            layer_height_px = self._tile_size_px[1] * self.layer_data_collection.scene_size_tile[1]
            self.layer_data_collection.scene_size_px = (layer_width_px, layer_height_px)
            if attributes["orientation"] == "orthogonal":
                self.current_tile_perspective = TILE_PERSPECTIVE.TOPDOWN
            elif attributes["orientation"] == "isometric":
                self.current_tile_perspective = TILE_PERSPECTIVE.DIMETRIC

        elif self.current_tag == "tileset":
            first_gid = int(attributes["firstgid"])
            #We have a seperate parser create the resource_data for the atlas since it is in a separate XML
            self.atlas_resource_datas.append(self.createAtlasResourceData(gamescene_resource_id = self.gamescene_resource_id,
                                                                          atlas_index = self.atlas_count,
                                                                          first_gid = first_gid,
                                                                          source_file = attributes["source"]))
            self.atlas_count +=1

        #Tilemap Layer
        elif self.current_tag == "layer":
            self.current_layer_type = "layer"
            self.current_layer_resource_data = RenderLayerResourceData(layer_level_id = self.current_layer_level,
                                                                       scene_layer_type = SCENE_LAYER_TYPE.RENDERABLE,
                                                                       scene_resource_datas = list(),
                                                                       #r_l_type can changeto Mixed when properties are parsed
                                                                       renderable_layer_type = RENDERABLE_LAYER_TYPE.ATLAS,
                                                                       tile_perspective = self.current_tile_perspective,
                                                                       is_needs_sorting = False)
            width_tiles = int(attributes["width"])
            height_tiles = int(attributes["height"])
            self.current_tiles = list()
            self.current_scene_resource_data = TilemapResourceData(gamescene_resource_id = self.gamescene_resource_id,
                                                                   s_resource_data_type = SRESOURCE_DATA_TYPE.TILEMAP,
                                                                   size_tiles = (width_tiles, height_tiles),
                                                                   tile_size_px = self._tile_size_px,
                                                                   tile_id_lists= self.current_tiles)
            self.current_layer_resource_data.addSceneResourceData(self.current_scene_resource_data)

        elif self.current_tag == "data":
            self.current_innerlayer_type = "data"

        #Panorama Layer
        elif self.current_tag == "imagelayer":
            self.current_layer_type = "imagelayer"
            self.current_layer_resource_data = RenderLayerResourceData(layer_level_id = self.current_layer_level,
                                                                       scene_layer_type = SCENE_LAYER_TYPE.RENDERABLE,
                                                                       scene_resource_datas = list(),
                                                                       renderable_layer_type = RENDERABLE_LAYER_TYPE.PANORAMA,
                                                                       tile_perspective = TILE_PERSPECTIVE.NA,
                                                                       is_needs_sorting = False)
        elif self.current_tag == "image":
            self.current_innerlayer_type = "image"
            if self.current_layer_type == "imagelayer":
                self.current_scene_resource_data = PanoramaResourceData(gamescene_resource_id = self.gamescene_resource_id,
                                                                        s_resource_data_type = SRESOURCE_DATA_TYPE.PANORAMA,
                                                                        image_ids = list(),
                                                                        images = list(),
                                                                        file_type = "",
                                                                        image_size_px = (0,0),
                                                                        world_offset_px = (0,0),
                                                                        visible_sections = (0,0),
                                                                        movement_speed = (0,0),
                                                                        scroll_speed = (0,0),
                                                                        animation_length_ms = (0,0))
        #When the tag is property, we will look for specific properties based in the layer we are creating
        elif self.current_tag == "property":
            if attributes["name"] == "isneedssorting":
                if attributes["value"] == "true":
                    self.current_is_needs_sorting = True
                else:
                    self.current_is_needs_sorting = False
                #If we have already begun to build the layer_resource_data, we may need to make some sorting updates
                if self.current_layer_resource_data is not None:
                    self.current_layer_resource_data.is_needs_sorting = self.current_is_needs_sorting
                    #If we are building an Atlas, but it needs sorting, this means we are building a mixed layer, which needs sorting
                    if self.current_layer_resource_data.renderable_layer_type == RENDERABLE_LAYER_TYPE.ATLAS and \
                            self.current_is_needs_sorting:
                        #mixed layers can have tiles and sprites on the same level, and will need to sort them
                        self.current_layer_resource_data.renderable_layer_type = RENDERABLE_LAYER_TYPE.MIXED

            #Handle the properties for a panorama layer
            elif self.current_layer_type == "imagelayer":
                #for most attributes need to parse a string into a list of strings, then convert those to ints
                if attributes["name"] == "animationlengthms":
                    self.current_scene_resource_data.animation_length_ms = int(attributes["value"])
                if attributes["name"] == "scrollspeed":
                    scroll_speed_strings = attributes["value"].split(",")
                    self.current_scene_resource_data.scroll_speed = \
                        stringListToIntList(scroll_speed_strings)
                if attributes["name"] == "movementspeed":
                    movement_speed_strings = attributes["value"].split(",")
                    self.current_scene_resource_data.movement_speed = \
                        stringListToIntList(movement_speed_strings)
                if attributes["name"] == "visiblesections":
                    visible_sections_strings = attributes["value"].split(",")
                    self.current_scene_resource_data.visible_sections = \
                        stringListToIntList(visible_sections_strings)
                if attributes["name"] == "worldoffsetpx":
                    world_offset_px_strings = attributes["value"].split(",")
                    self.current_scene_resource_data.world_offset_px= \
                        stringListToIntList(world_offset_px_strings)
                if attributes["name"] == "imagesizepx":
                    image_size_px_strings = attributes["value"].split(",")
                    self.current_scene_resource_data.image_size_px= \
                        stringListToIntList(image_size_px_strings)
                if attributes["name"] == "filetype":
                    self.current_scene_resource_data.file_type = attributes["value"]
                if attributes["name"] == "imageids":
                    image_ids_strings = attributes["value"].split(",")
                    self.current_scene_resource_data.image_ids= \
                        stringListToIntList(image_ids_strings)

            elif self.current_layer_type == "layer": #layer is a generic sounding name but is always a tilemap layer
                #We could have either ATLAS or MIXED for this layer
                if attributes["name"] == "renderablelayertype":
                    renderable_layer_type = RENDERABLE_LAYER_TYPE(int(attributes["value"]))
                    self.current_layer_resource_data.renderable_layer_type = renderable_layer_type
                    if renderable_layer_type == RENDERABLE_LAYER_TYPE.MIXED:
                        self.current_layer_resource_data.is_needs_sorting = True
                    elif renderable_layer_type == RENDERABLE_LAYER_TYPE.ATLAS:
                        self.current_layer_resource_data.is_needs_sorting = False

            #Several layers use the generic 'object group' type from TMX
            elif self.current_layer_type == "objectgroup": #These properties will help define the purpose of this object layer
                if attributes["name"] == "scenelayertype":
                    self.current_scene_layer_type = SCENE_LAYER_TYPE(int(attributes["value"]))
                if attributes["name"] == "renderablelayertype":
                    self.current_renderable_layer_type = RENDERABLE_LAYER_TYPE(int(attributes["value"]))

        #Object Layer
        elif self.current_tag == "objectgroup":
            self.current_layer_type = "objectgroup"

        elif self.current_tag == "object":
            self.current_innerlayer_type = "object"

        elif self.current_tag == "point":
            if self.current_innerlayer_type == "object":
                self.current_object_type = "point"

        elif self.current_tag == "ellipse":
            if self.current_innerlayer_type == "object":
                self.current_object_type = "ellipse"

    # Call when an elements ends
    def endElement(self, tag):
        #If we have gotten the end tag of the image layer, scene_resource_data is created
        if tag == "image":
            if self.current_layer_type == "imagelayer": #then it's a panorama
                #We are adding the reference here, but it still hase some properties to be loaded
                self.current_layer_resource_data.addSceneResourceData(self.current_scene_resource_data)

        #Our panorama layer is complete, and the properties have been loaded to our image
        #This assumes we only had 1 image tag in the image layer (per Tiled's xml structure)
        elif tag == 'imagelayer':
            self.current_layer_type = ""
            images = list()
            file_type = self.current_scene_resource_data.file_type
            #Need to use the image loaded to get the actual image from the id's
            for image_id in self.current_scene_resource_data.image_ids:
                images.append(TiledXmlHandler.load_panorama_image(image_id = image_id,
                                                                  file_type = file_type))
            self.current_scene_resource_data.images = images
            #This layer is completed and added to the dictionary
            self.layer_resource_datas[self.current_layer_level] = self.current_layer_resource_data
            self.current_layer_level+=1
            self.resetLayerData()

        #The object layer is complete, will need to check current types/properties to build the layer
        elif tag == 'objectgroup':
            if self.current_scene_layer_type == SCENE_LAYER_TYPE.RENDERABLE:
                if self.current_renderable_layer_type == RENDERABLE_LAYER_TYPE.ATLAS:
                    pass

                elif self.current_renderable_layer_type == RENDERABLE_LAYER_TYPE.PANORAMA: #TODO - we don't get here currently, remove?
                    self.current_layer_resource_data = RenderLayerResourceData(layer_level_id = self.current_layer_level,
                                                                               scene_layer_type = self.current_scene_layer_type,
                                                                               scene_resource_datas = list(),
                                                                               renderable_layer_type = self.current_renderable_layer_type,
                                                                               tile_perspective = self.current_tile_perspective,
                                                                               is_needs_sorting = self.current_is_needs_sorting)
                    self.layer_resource_datas[self.current_layer_level] = self.current_layer_resource_data
                    self.current_layer_level += 1

                elif self.current_renderable_layer_type == RENDERABLE_LAYER_TYPE.IMAGE: #A sprite only layer has been created
                    self.current_layer_resource_data = RenderLayerResourceData(layer_level_id = self.current_layer_level,
                                                                               scene_layer_type = self.current_scene_layer_type,
                                                                               scene_resource_datas = list(),
                                                                               renderable_layer_type = self.current_renderable_layer_type,
                                                                               tile_perspective = self.current_tile_perspective,
                                                                               is_needs_sorting = self.current_is_needs_sorting)
                    self.layer_resource_datas[self.current_layer_level] = self.current_layer_resource_data
                    self.current_layer_level += 1

                elif self.current_renderable_layer_type == RENDERABLE_LAYER_TYPE.MIXED:
                    pass
            elif self.current_scene_layer_type == SCENE_LAYER_TYPE.PHYSICAL:
                pass
            elif self.current_scene_layer_type == SCENE_LAYER_TYPE.ENVIRONMENT:
                pass
            elif self.current_scene_layer_type == SCENE_LAYER_TYPE.EVENT:
                pass
            #reset the current types
            self.resetLayerData()

        elif tag == 'layer': #Is already built, and may be an atlas or a mixed layer
            self.layer_resource_datas[self.current_layer_level] = self.current_layer_resource_data
            self.current_layer_level+=1
            self.resetLayerData()

        elif tag == 'data':
            tile_height = self.current_scene_resource_data.size_tiles[1]
            #if this isn't true, there is an issue with this scenes xml data (or the code)
            assert(tile_height == len(self.current_tiles))

    # Call when a character is read
    def characters(self, content):
        if self.current_innerlayer_type == 'data':
            try:
                tile_width = self.current_scene_resource_data.size_tiles[0]
                if len(content) >= tile_width: #will actually be much longer due to commas and multi-digit values
                    row = content.split(',') #a comma seperated string converted to an array
                    if row[-1] == "":
                        row = row[0:len(row)-1] #a trailing comma leaves us with an empty index
                    row = [int(numeric_string) for numeric_string in row] #convert the string array to int array

                    self.current_tiles.append(row)
            except Exception as e:
                print("Exception caught while parsing tmx file")
                print("content: " + str(content))
                print(e)

    #Call another XML parser to read the atlas xml file and create an AtlasResourceData
    def createAtlasResourceData(self,
                                gamescene_resource_id, #int
                                atlas_index, #int
                                first_gid, #int
                                source_file): #string
        # create an XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # override the default ContextHandler
        atlas_xml_handler = AtlasXmlHandler(gamescene_resource_id = gamescene_resource_id,
                                            atlas_index = atlas_index,
                                            first_gid = first_gid)
        parser.setContentHandler(atlas_xml_handler)
        parser.parse(SCENE_ROOT_PATH + SCENE_ATLAS_PATH + str(source_file)) #the extension of .tsx is in the path
        return atlas_xml_handler.getAtlasResourceData()

    #After parser finishes grabs the completed data here,
    def getLayerDataCollection(self):
        return self.layer_data_collection

    #Called on end tag for each layer
    def resetLayerData(self):
        self.current_scene_layer_type = SCENE_LAYER_TYPE.NA
        self.current_renderable_layer_type = RENDERABLE_LAYER_TYPE.NA
        self.current_is_needs_sorting = False
        self.current_tiles = None
        self.current_layer_resource_data = None
        self.current_scene_resource_data = None
        self.current_layer_type = ""
        self.current_innerlayer_type = ""
        self.current_object_type = ""

#Utilized by the SceneJsonParser to parse the atlast made in TILED
#Must export the atlas as JSON
class AtlasJsonParser:
    load_atlas_image = None

    def __init__(self):#int
        pass

    def createAtlasResourceData(self,
                                gamescene_resource_id,  # int
                                source, #string
                                atlas_index,  # int
                                first_gid): #int
        #we want to strip down to just the name of the tileset, and change the extension to ".json"
        filename = source.split('/')[-1]
        filename = filename.split('.')[0] + TILED_JSON_EXTENSION
        file = open(SCENE_ROOT_PATH + SCENE_ATLAS_PATH + filename)
        json_dict = json.loads(file.read())
        file.close()

        image_path = json_dict["image"]  # eg "<path>\\#######.png" - we want the integer value of #####, and the filetype
        image_id = int(image_path.split('/')[-1].split(".")[0])
        file_type = image_path.split('/')[-1].split(".")[1]
        image = AtlasXmlHandler.load_atlas_image(image_id=image_id,
                                                 file_type=file_type)
        animated_tile_resource_data = dict() #{int : AnimatedTileResourceData} - keyed on gid of first tile
        floating_tile_gids = dict() #{int : bool}
        #Get the animated and floating tiles.  A tile can be both floating and animated, but this will be
        #defined in 2 seperate dictionary entries
        for tile in json_dict["tiles"]:
            if tile.get("animation") is not None:
                tile_gids = list()
                durations = list()
                animated_gid = tile["id"]
                for frame in tile["animation"]:
                    tile_gids.append(int(frame["tileid"]))
                    durations.append(int(frame["duration"]))
                animated_tile_resource_data[animated_gid] = AnimatedTileResourceData(tile_gids = tuple(tile_gids),
                                                                                     durations = tuple(durations))
            if tile.get("properties") is not None:
                for property in tile["properties"]:
                    if property.get("name") == "floating_tile":
                        floating_tile_gids[tile["id"]] = True

        return AtlasResourceData(gamescene_resource_id = gamescene_resource_id,
                                 s_resource_data_type = SRESOURCE_DATA_TYPE.ATLAS,
                                 atlas_index = atlas_index,
                                 first_gid = first_gid,
                                 tile_size_px = tuple((int(json_dict['tilewidth']),int(json_dict['tileheight']))),
                                 tile_count = int(json_dict['tilecount']),
                                 numb_columns = int(json_dict['columns']),
                                 floating_tile_gids = floating_tile_gids,
                                 image_id = image_id,
                                 image = image,
                                 file_type = file_type,
                                 animated_tile_resource_datas = animated_tile_resource_data)

#class to parse a map created in Tiled.  Must export the map as JSON (Tiled saves in an xml format)
#The JSON is simpler to parse than the XML, so the XML parser is deprecated
class SceneJsonParser:
    #func ptr for the SpriteImageManager load image method
    load_panorama_image = None

    def __init__(self):#int
        self._atlas_json_parser = AtlasJsonParser()
        self._current_gamescene_resource_id = 0

    def createLayerDataCollection(self,
                                  gamescene_resource_id):
        self._current_gamescene_resource_id = gamescene_resource_id
        file = open(SCENE_ROOT_PATH + str(gamescene_resource_id) + TILED_JSON_EXTENSION)
        json_dict = json.loads(file.read())
        file.close()

        #Scene Properties
        scene_size_tile = (int(json_dict["width"]), int(json_dict["height"]))
        tile_size_px = (int(json_dict["tilewidth"]), int(json_dict["tileheight"]))
        layer_width_px = tile_size_px[0] * scene_size_tile[0]
        layer_height_px = tile_size_px[1] * scene_size_tile[1]
        scene_size_px = (layer_width_px, layer_height_px)
        tile_perspective = TILE_PERSPECTIVE.TOPDOWN # json_dict["orientation"] == "orthogonal":
        if json_dict["orientation"] == "isometric":
            tile_perspective = TILE_PERSPECTIVE.DIMETRIC

        #Load Atlas's
        atlas_resource_datas = list() #store each atlas resource data by index
        atlas_count = 0
        for tileset in json_dict["tilesets"]:
            atlas_resource_data = self._atlas_json_parser.createAtlasResourceData(atlas_index = atlas_count,
                                                                                  first_gid = int(tileset["firstgid"]),
                                                                                  gamescene_resource_id = gamescene_resource_id,
                                                                                  source = tileset["source"])
            atlas_resource_datas.append(atlas_resource_data)
            atlas_count+=1

        #Create Layers
        current_layer_level = 0
        layer_resource_datas = dict() #store each layer created by layer_level_id
        for layer in json_dict["layers"]:
            if layer["type"] == "tilelayer": #tilemap
                layer_resource_datas[current_layer_level] = self._createTilemapLayer(tile_size_px = tile_size_px,
                                                                                     tile_perspective = tile_perspective,
                                                                                     current_layer_level = current_layer_level,
                                                                                     layer = layer)
                current_layer_level +=1

            elif layer["type"] == "imagelayer": #panorama (either BG or FG)
                layer_resource_datas[current_layer_level] = self._createPanoramaLayer(current_layer_level = current_layer_level,
                                                                                      layer = layer)
                current_layer_level +=1

            #This is a WIP - eventually will be adding and further parsing types of object layers
            elif layer["type"] == "objectgroup":
                #All of this is just a temporary hack to add the spriteonly placeholder layer
                spriteonlylayer = False
                if layer.get("properties") is not None:
                    for property in layer["properties"]:
                        if property["name"] == "renderablelayertype":
                            if property["value"] == 2:
                                spriteonlylayer = True
                if spriteonlylayer:
                    layer_resource_datas[current_layer_level] = RenderLayerResourceData(layer_level_id = current_layer_level,
                                                                                        scene_layer_type = SCENE_LAYER_TYPE.RENDERABLE,
                                                                                        scene_resource_datas = list(),
                                                                                        renderable_layer_type = RENDERABLE_LAYER_TYPE.IMAGE,
                                                                                        tile_perspective = TILE_PERSPECTIVE.TOPDOWN,
                                                                                        is_needs_sorting = True)
                    current_layer_level +=1

        #Build the collection and return it
        layer_data_collection = LayerDataCollection(gamescene_resource_id = gamescene_resource_id,
                                                    atlas_resource_datas = atlas_resource_datas,
                                                    layer_resource_datas = layer_resource_datas)
        layer_data_collection.scene_size_px = scene_size_px
        layer_data_collection.scene_size_tile = scene_size_tile
        return layer_data_collection

    def _createTilemapLayer(self,
                            tile_size_px,
                            tile_perspective,
                            current_layer_level, #int
                            layer): #dict - from JSON
        size_tiles = (int(layer["width"]), int(layer["height"]))
        tile_id_lists = list()
        flat_tile_list = layer["data"] #we need to convert this to a 2d list (tiles in rows)
        row_count = 0
        tile_count = 0
        while row_count < size_tiles[1]:
            tile_row = list()
            col_count = 0
            while col_count < size_tiles[0]:
                tile_row.append(flat_tile_list[tile_count])
                col_count+=1
                tile_count+=1
            tile_id_lists.append(tuple(tile_row))
            row_count+=1
        assert(tile_count == size_tiles[0]*size_tiles[1])
        assert(len(tile_id_lists) == size_tiles[1])
        assert(len(tile_id_lists[0]) == size_tiles[0])
        assert(len(tile_id_lists[-1]) == size_tiles[0])

        tilemap_resource_data = TilemapResourceData(gamescene_resource_id = self._current_gamescene_resource_id,
                                                    s_resource_data_type = SRESOURCE_DATA_TYPE.TILEMAP,
                                                    size_tiles = tuple(size_tiles),
                                                    tile_size_px = tuple(tile_size_px),
                                                    tile_id_lists = tuple(tile_id_lists))

        render_layer_resource_data = RenderLayerResourceData(layer_level_id = current_layer_level,
                                                             scene_layer_type = SCENE_LAYER_TYPE.RENDERABLE,
                                                             scene_resource_datas = [tilemap_resource_data],
                                                             # r_l_type can changeto Mixed when properties are parsed
                                                             renderable_layer_type = RENDERABLE_LAYER_TYPE.ATLAS,
                                                             tile_perspective = tile_perspective,
                                                             # can change to True when properties are parsed
                                                             is_needs_sorting = False)

        self._loadTilemapProperties(render_layer_resource_data=render_layer_resource_data,
                                    properties=layer["properties"])

        return render_layer_resource_data

    def _loadTilemapProperties(self,
                               render_layer_resource_data, #RenderLayerResourceData
                               properties): #dict
        is_needs_sorting = False
        renderable_layer_type = RENDERABLE_LAYER_TYPE.ATLAS
        for property in properties:
            if property["name"] == "renderablelayertype":
                renderable_layer_type = RENDERABLE_LAYER_TYPE(int(property["value"]))
                if renderable_layer_type == RENDERABLE_LAYER_TYPE.MIXED:
                    is_needs_sorting = True
        render_layer_resource_data.renderable_layer_type = renderable_layer_type
        render_layer_resource_data.is_needs_sorting = is_needs_sorting

    def _createPanoramaLayer(self,
                             current_layer_level, #int
                             layer): #dict - from JSON
        images = list() #generated after we load properties
        panorama_resource_data = PanoramaResourceData(gamescene_resource_id=self._current_gamescene_resource_id,
                                                      s_resource_data_type=SRESOURCE_DATA_TYPE.PANORAMA,
                                                      image_ids=list(),
                                                      images= images ,
                                                      file_type="",
                                                      image_size_px=(0, 0),
                                                      world_offset_px=(0, 0),
                                                      visible_sections=(0, 0),
                                                      movement_speed=(0, 0),
                                                      scroll_speed=(0, 0),
                                                      animation_lengths_ms=(0, 0))

        self._loadPanoramaProperties(panorama_resource_data=panorama_resource_data,
                                     properties=layer["properties"])

        for image_id in panorama_resource_data.image_ids:
            images.append(SceneJsonParser.load_panorama_image(image_id=image_id,
                                                              file_type=panorama_resource_data.file_type))
            panorama_resource_data.images = tuple(images)

        layer_resource_data = RenderLayerResourceData(layer_level_id=current_layer_level,
                                                      scene_layer_type=SCENE_LAYER_TYPE.RENDERABLE,
                                                      scene_resource_datas=[panorama_resource_data],
                                                      renderable_layer_type=RENDERABLE_LAYER_TYPE.PANORAMA,
                                                      tile_perspective=TILE_PERSPECTIVE.NA,
                                                      is_needs_sorting=False)
        return layer_resource_data

    def _loadPanoramaProperties(self,
                                panorama_resource_data, #PanoramaResourceData
                                properties): #dict
        for property in properties:
            if property["name"] == "animationlengthsms":
                panorama_resource_data.animation_lengths_ms = tuple(stringListToIntList(property["value"].split(",")))
            elif property["name"] == "filetype":
                panorama_resource_data.file_type = property["value"]
            elif property["name"] == "imageids":
                panorama_resource_data.image_ids = tuple(stringListToIntList(property["value"].split(",")))
            elif property["name"] == "imagesizepx":
                panorama_resource_data.image_size_px = tuple(stringListToIntList(property["value"].split(",")))
            elif property["name"] == "movementspeed":
                panorama_resource_data.movement_speed = tuple(stringListToIntList(property["value"].split(",")))
            elif property["name"] == "scrollspeed":
                panorama_resource_data.scroll_speed = tuple(stringListToIntList(property["value"].split(",")))
            elif property["name"] == "visiblesections":
                panorama_resource_data.visible_sections = tuple(stringListToIntList(property["value"].split(",")))
            elif property["name"] == "worldoffsetpx":
                panorama_resource_data.world_offset_px = tuple(stringListToIntList(property["value"].split(",")))

#DEPRECATE IN FAVOR OF THE JSON PARSER
class SceneXmlParser:
    def __init__(self):
        pass

    def createLayerDataCollection(self,
                                  gamescene_resource_id):
        # create an XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # override the default ContextHandler
        tiled_xml_handler = TiledXmlHandler(gamescene_resource_id)
        parser.setContentHandler(tiled_xml_handler)
        parser.parse(SCENE_ROOT_PATH + str(gamescene_resource_id) + TILED_XML_EXTENSION)
        return tiled_xml_handler.getLayerDataCollection()

#Generic Parent Class for Data for a scene component
#Each will be seperatly stored by the manager for quick loading (every scene component has a unique id)
class SceneResourceData(ResourceData):
    def __init__(self,
                 gamescene_resource_id, #int
                 s_resource_data_type): #SRESOURCE_DATA_TYPE
        super(SceneResourceData, self).__init__()
        self.gamescene_resource_id = gamescene_resource_id
        self.s_resource_data_type = s_resource_data_type

class PanoramaResourceData(SceneResourceData):
    def __init__(self,
                 gamescene_resource_id,  # int
                 s_resource_data_type,  # SRESOURCE_DATA_TYPE
                 image_ids, #[int]
                 images,  #(pygame.image,)
                 file_type,  # string (e.g. png, jpg, bmp,...)
                 image_size_px,  # (int, int,)
                 world_offset_px,  # (int,int,)
                 visible_sections,  # (int,)
                 movement_speed,  # (int,int,)
                 scroll_speed,  # (int, int, int, int,)
                 animation_lengths_ms):  # (int,)
        super(PanoramaResourceData, self).__init__(gamescene_resource_id = gamescene_resource_id,
                                                   s_resource_data_type = s_resource_data_type)
        self.image_ids = image_ids
        self.images = images
        self.file_type = file_type
        self.image_size_px = image_size_px
        self.world_offset_px = world_offset_px
        self.visible_sections = visible_sections
        self.movement_speed = movement_speed
        self.scroll_speed = scroll_speed
        self.animation_lengths_ms = animation_lengths_ms

#This is going to be used to generate individual tile instances,
#which will each have a reference to their respective atlas (for image and animation data)
class TilemapResourceData(SceneResourceData):
    def __init__(self,
                 gamescene_resource_id,  # int
                 s_resource_data_type,  # SRESOURCE_DATA_TYPE
                 size_tiles,  #(int,int,)
                 tile_size_px, #(int, int,)
                 tile_id_lists): #((int,),) - the 'gid' value if each tile (to eventually be a converted to coordinates)
        super(TilemapResourceData, self).__init__(gamescene_resource_id = gamescene_resource_id,
                                                  s_resource_data_type = s_resource_data_type)
        self.size_tiles = size_tiles
        self.tile_id_lists = tile_id_lists
        self.tile_size_px = tile_size_px


#Stored in the AtlasResourceData
class AnimatedTileResourceData:
    def __init__(self,
                 tile_gids,  #(int,)
                 durations): #(int,) - in milliseconds
        self.tile_gids = tile_gids
        self.durations = durations

class AtlasResourceData(SceneResourceData):
    def __init__(self,
                 gamescene_resource_id,  #int
                 s_resource_data_type,  # SRESOURCE_DATA_TYPE
                 atlas_index, #int
                 first_gid,
                 tile_size_px, #(int, int,)
                 tile_count, #int
                 numb_columns, #int
                 floating_tile_gids, #{int : bool}
                 image_id, #int
                 image, #pygame.image
                 file_type, #string - (png, bmp, etc)
                 animated_tile_resource_datas): #dict{int : AnimatedTileResourceData] - keyed on the gid of the first tile in sequence
        super(AtlasResourceData, self).__init__(gamescene_resource_id = gamescene_resource_id, #will the index of this atlas for this scene
                                                s_resource_data_type = s_resource_data_type)
        self.atlas_index = atlas_index
        self.first_gid = first_gid
        self.tile_size_px = tile_size_px
        self.tile_count = tile_count
        self.numb_columns = numb_columns
        self.floating_tile_gids = floating_tile_gids
        self.image_id = image_id
        self.image = image
        self.file_type = file_type
        self.animated_tile_resource_datas = animated_tile_resource_datas



#Contains layer type information, and the ScenDataCollection
#stored by the scene_id/layer_id combo
class LayerResourceData(ResourceData):
    def __init__(self,
                 layer_level_id, #int
                 scene_layer_type, #SCENE_LAYER_TYPE
                 scene_resource_datas): #[SceneResourceData]
        super(LayerResourceData, self).__init__()
        self.layer_level_id = layer_level_id
        self.scene_layer_type = scene_layer_type
        self.scene_resource_datas = scene_resource_datas

    def addSceneResourceData(self,
                             scene_resource_data): #SceneResourceData
        self.scene_resource_datas.append(scene_resource_data)

class RenderLayerResourceData(LayerResourceData):
    def __init__(self,
                 layer_level_id,  #int
                 scene_layer_type,  #SCENE_LAYER_TYPE
                 scene_resource_datas, #[SceneResourceData]
                 renderable_layer_type, #RENDERABLE_LAYER_TYPE
                 tile_perspective, #TILE_PERSPECTIVE
                 is_needs_sorting): #bool
        super(RenderLayerResourceData, self).__init__(layer_level_id = layer_level_id,
                                                      scene_layer_type = scene_layer_type,
                                                      scene_resource_datas = scene_resource_datas)
        self.renderable_layer_type = renderable_layer_type
        self.tile_perspective = tile_perspective
        self.is_needs_sorting = is_needs_sorting

# A Scene ID, a list of AtlastResources, and a dict of LayerResourceData for the scene
#stored by the scene_id
class LayerDataCollection:
    def __init__(self,
                 gamescene_resource_id,  #int
                 atlas_resource_datas, #[AtlasResourceData]
                 layer_resource_datas):  #{layer_level_id : LayerResourceData}
        self.gamescene_resource_id = gamescene_resource_id
        self.atlas_resource_datas = atlas_resource_datas
        self.layer_resource_datas = layer_resource_datas
        self.scene_size_px = (0,0)
        self.scene_size_tile = (0,0)

#_element_ids refer to a scene_collection, or a component
#self._element_tag_ids = dict() #{int: int} - can refer to a scene_collection, or a scene_component
#every time a new scene, layer or component is loaded, generate a new element ID.
#element ID's are unique and dynamic. Can track specific ones by a tag
class SceneResourceManager(ResourceManager):
    #SceneHandler.createRenderLayer
    create_scene_layer = None
    #ComponentSystem.createComponent
    create_component_methods = dict() #{SRESOURCE_DATA_TYPE : func* createComponent}
    #ComponentSystem.getSceneComponentPtrs
    get_scene_component_methods = dict() #{SRESOURCE_DATA_TYPE : func* getSceneComponentPtrs}
    #TilemapComponentSystem.createAtlas
    create_atlas = None

    def __init__(self):
        super(SceneResourceManager, self).__init__()
        #The object which will take a resource id and return layer_data_collections
        #self._resource_loader = SceneXmlParser() DEPRECATED
        self._resource_loader = SceneJsonParser()
        self._layer_data_collections = dict() #{int : LayerDataCollection} - key = gamescene_resource_id

    #load all layers and components for a scene, and return the element ID for this scene
    def spawnScene(self,
                   gamescene_resource_id): #int
        #loads any of the resource datas that aren't already loaded
        self._loadLayerDataCollection(gamescene_resource_id)
        #generates a new scene from the loaded resource data
        #returns the unique element id's in this form:
        #{layer_level_id1: [layer_element_id1, component_id1, component_id2,...], layer_level_id2 : [layer_element_id2, component_id1, component_id2,...],...}
        new_element_ids = self._createScene(gamescene_resource_id)
        return new_element_ids

    def spawnLayer(self,
                   layer_level_id,
                   l_resource_id):
        pass

    def spawnSceneComponent(self,
                            layer_level_id,
                            s_resource_id):
        pass

    #The resource_datas for the create methods are already existing, because the load was called first
    def _createScene(self,
                     gamescene_resource_id):
        new_element_ids = dict()
        layer_data_collection = self._layer_data_collections[gamescene_resource_id]
        for atlas_resource_data in layer_data_collection.atlas_resource_datas:
            self._createAtlas(gamescene_resource_id = gamescene_resource_id,
                              atlas_resource_data = atlas_resource_data)
        for layer_level_id, layer_resource_data in layer_data_collection.layer_resource_datas.items():
            new_layer_element_ids = list()
            layer_element_id = self.createElementId()
            new_layer_element_ids.append(layer_element_id)
            new_layer_element_ids += self._createLayer(layer_element_id = layer_element_id,
                                                       layer_level_id = layer_level_id,
                                                       layer_resource_data = layer_resource_data)
            new_element_ids[layer_level_id] = new_layer_element_ids

        return new_element_ids

    def _createAtlas(self,
                     gamescene_resource_id,
                     atlas_resource_data):
        SceneResourceManager.create_atlas(gamescene_resource_id = gamescene_resource_id,
                                          atlas_resource_data = atlas_resource_data)

    def _createLayer(self,
                     layer_element_id,  #int - the dynamically created if for the layer
                     layer_level_id,  #int - the number that determines the order of the layer
                     layer_resource_data): #LayerResourceData
        SceneResourceManager.create_scene_layer(layer_element_id = layer_element_id,
                                                layer_level_id = layer_level_id,
                                                resource_data = layer_resource_data)
        new_element_ids = list()
        for scene_resource_data in layer_resource_data.scene_resource_datas:
            component_element_id = self._createComponent(scene_resource_data = scene_resource_data,
                                                         layer_element_id = layer_element_id,
                                                         layer_level_id = layer_level_id)
            new_element_ids.append(component_element_id)

        return new_element_ids

    def _createComponent(self,
                         scene_resource_data,
                         layer_element_id,
                         layer_level_id):
        component_element_id = self.createElementId()
        #We create the component first
        SceneResourceManager.create_component_methods[scene_resource_data.s_resource_data_type](
            scene_element_id = component_element_id,
            layer_element_id = layer_element_id,
            layer_level_id = layer_level_id,
            resource_data = scene_resource_data)

        #After the component is created, we will ask the component system to send back the layer pointers
        scene_components = SceneResourceManager.get_scene_component_methods[scene_resource_data.s_resource_data_type]\
            (component_element_id = component_element_id)

        for scene_component in scene_components:
            ResourceManager.add_component_to_layer(layer_level_id = layer_level_id,
                                                   scene_component = scene_component)
        return component_element_id

    #This is the data collection which represents an entire scene
    def _loadLayerDataCollection(self,
                                 gamescene_resource_id): #int
        # if this collection is already created, do nothing
        if self._layer_data_collections.get(gamescene_resource_id) is None:
            self._layer_data_collections[gamescene_resource_id] = \
                self._resource_loader.createLayerDataCollection(gamescene_resource_id)


#This will compare 2 layerdatacollections and determine if they are identical (as of development on 10/22/19)
def temp_testJsonLoad(a, b):
    def resource_test(a,b):
        if a.resource_data_type == SRESOURCE_DATA_TYPE.TILEMAP:
            assert (a.resource_id == b.resource_id)
            assert (a.resource_data_type == b.resource_data_type)
            assert (a.size_tiles == b.size_tiles)
            assert (a.tile_size_px == b.tile_size_px)
            assert (len(a.tile_id_lists) == len(b.tile_id_lists))
            assert (len(a.tile_id_lists[0]) == len(b.tile_id_lists[0]))
            assert (len(a.tile_id_lists[-1]) == len(b.tile_id_lists[-1]))
            assert (len(a.tile_id_lists[5]) == len(b.tile_id_lists[5]))

            row_count = len(a.tile_id_lists)
            col_count = len(a.tile_id_lists[0])
            i = 0
            j = 0
            while i<row_count:
                j = 0
                while j < col_count:
                    assert(a.tile_id_lists[i][j] == b.tile_id_lists[i][j])
                    j+=1
                i+=1

        elif a.resource_data_type == SRESOURCE_DATA_TYPE.PANORAMA:
            assert (a.resource_id == b.resource_id)
            assert (a.resource_data_type == b.resource_data_type)
            assert (a.image_ids == b.image_ids)
            assert (len(a.images) == len(b.images))
            img_count = len(a.images)
            i = 0
            while i < img_count:
                assert(a.images[i] == b.images[i])
                i+=1
            assert (a.file_type == b.file_type)
            assert (a.image_size_px == b.image_size_px)
            assert (a.world_offset_px == b.world_offset_px)
            assert (a.visible_sections == b.visible_sections)
            assert (a.movement_speed == b.movement_speed)
            assert (a.scroll_speed == b.scroll_speed)
            assert (a.animation_length_ms == b.animation_length_ms)

    def atlas_test(a,b):
        assert (a.resource_id == b.resource_id)
        assert (a.resource_data_type == b.resource_data_type)
        assert (a.atlas_index == b.atlas_index)
        assert (a.first_gid == b.first_gid)
        assert (a.tile_size_px == b.tile_size_px)
        assert (a.tile_count == b.tile_count)
        assert (a.numb_columns == b.numb_columns)
        assert (a.floating_tile_gids == b.floating_tile_gids)
        assert (a.image_id == b.image_id)
        assert (a.image == b.image)
        assert (a.file_type == b.file_type)
        assert (len(a.animated_tile_resource_datas) == len(b.animated_tile_resource_datas))
        for gid in list(a.animated_tile_resource_datas.keys()):
            assert(a.animated_tile_resource_datas[gid].tile_gids == b.animated_tile_resource_datas[gid].tile_gids)
            assert(a.animated_tile_resource_datas[gid].durations == b.animated_tile_resource_datas[gid].durations)

    def layer_test(a,b):
        assert (a.resource_id == b.resource_id)
        assert (a.resource_data_type == b.resource_data_type)
        assert (a.renderable_layer_type == b.renderable_layer_type)
        assert (a.tile_perspective == b.tile_perspective)
        assert (a.is_needs_sorting == b.is_needs_sorting)
        assert (len(a.scene_resource_datas) == len(b.scene_resource_datas))
        rd_count = len(a.scene_resource_datas)
        i = 0
        while i < rd_count:
            resource_test(a.scene_resource_datas[i], b.scene_resource_datas[i])
            i+=1

    assert(a.gamescene_resource_id == b.gamescene_resource_id)
    assert(a.scene_size_px == b.scene_size_px)
    assert(a.scene_size_tile == b.scene_size_tile)
    assert(len(a.atlas_resource_datas) == len(b.atlas_resource_datas))
    assert(len(a.layer_resource_datas) == len(b.layer_resource_datas))
    atlas_count = len(a.atlas_resource_datas)
    i = 0
    while i < atlas_count:
        atlas_test(a.atlas_resource_datas[i], b.atlas_resource_datas[i])
        i+=1

    for layer_level_id in list(a.layer_resource_datas.keys()):
        layer_test(a.layer_resource_datas[layer_level_id],b.layer_resource_datas[layer_level_id])









