from component_system import SceneComponentSystem, SceneComponent, Renderable
import sys
sys.path.append("parameters\\")
import TIMING_PARAM

class TileInstance(Renderable):
    def __init__(self,
                 parent_component,  #TilemapComponent
                 component_element_id,  #int
                 layer_level_id,  #int
                 subcomponent_index,  #int
                 atlas_image,  #pygame.image
                 tile_size_px,  #(int, int,)
                 atlas_coordinates_px,  #(int, int,)
                 world_position_tile, #(int,int,)
                 world_coordinates_px, #(int, int,)
                 ground_position_px): #(int, int,)
        super(Renderable, self).__init__(parent_component = parent_component,
                                         component_element_id=component_element_id,
                                         layer_level_id = layer_level_id,
                                         subcomponent_index = subcomponent_index)
        self._atlas_image = atlas_image
        self._tile_size_px = tile_size_px
        self._world_position_tile = world_position_tile
        self._atlas_coordinates_px = atlas_coordinates_px #This is the x,y origin of the tile on the atlast
        self._world_coordinates_px = world_coordinates_px #The pixel position of top left corner in world map
        self._ground_position_px = ground_position_px

        self._is_floating = False

        #We need to send the position on the atlas, and the size of the tile to the renderer
        self._atlas_coordinates_px = list(self._atlas_coordinates_px) + list(self._tile_size_px)
        self._atlas_coordinates_px = tuple(self._atlas_coordinates_px)
        self._current_position_px = list() #calculated every frame

    def setFloating(self,
                    is_floating): #bool
        self._is_floating = is_floating

    def isFloating(self):
        return self._is_floating

    def getImage(self):
        return self._atlas_image

    #This will be called when the renderer is ready to display the image
    def calculateCoordinates(self,
                             camera_offset, #[int, int]
                             lag_normalized): #float [0,1) #
        self._current_position_px = (self._world_coordinates_px[0] - camera_offset[0],
                                     self._world_coordinates_px[1] - camera_offset[1],
                                     0) #we won't ever have a Z component for a tile

    def getImageCoordinates(self):
        return self._atlas_coordinates_px

    def getScreenCoordinates(self):
        return self._current_position_px

    def kill(self):
        pass #TODO

    def getWorldPositionTile(self):
        return self._world_position_tile

    def getWorldCoordinates(self):
        return self._world_coordinates_px

    def setGroundPositionPx(self,
                            ground_position_px):
        self._ground_position_px = ground_position_px

    def getGroundPositionPx(self):
        return self._ground_position_px


#Tracks how long each tile frame lasts, and the coordinates on the atlas for each frame
class AnimatedTileData:
    def __init__(self,
                 tile_coordinates,  #((int,int,),) - list of XY pairs which are origin of tiles on atlas
                 tile_size_px, #(int, int,)
                 durations, #(int,) - list of durations of each coordinate pair in ms
                 numb_frames):
        self.tile_coordinates = tile_coordinates
        self.tile_size_px = tile_size_px
        self.durations = durations
        self.numb_frames = numb_frames

        #we need each set of coordinates to have the tile size appended to it
        self.tile_coordinates = list(self.tile_coordinates)
        i = 0
        while i < numb_frames:
            self.tile_coordinates[i] = list(self.tile_coordinates[i])
            self.tile_coordinates[i] += list(self.tile_size_px)
            self.tile_coordinates[i] = tuple(self.tile_coordinates[i])
            i+=1
        self.tile_coordinates = tuple(self.tile_coordinates)

    def getDuration(self,
                    frame_index): #int
        return self.durations[frame_index]

    def getImageCoordinates(self,
                            frame_index): #int
        return self.tile_coordinates[frame_index]

    def getNumbFrames(self):
        return self.numb_frames

class AnimatedTileInstance(TileInstance):
    def __init__(self,
                 parent_component,  # TilemapComponent
                 component_element_id,  #int
                 layer_level_id,  #int
                 subcomponent_index,  #int
                 atlas_image,  #pygame.image
                 tile_size_px,  #[int,int]
                 atlas_coordinates_px,  #[int, int] - This will change with animation, so it is a List not a Tuple
                 world_position_tile, #(int,int,)
                 world_coordinates_px,  #(int, int,)
                 ground_position_px, #(int, int,)
                 animated_tile_data): #AnimatedTileData (as a pointer, multiple tiles can share a tiledata)
        super(AnimatedTileInstance, self).__init__(parent_component = parent_component,
                                                   component_element_id = component_element_id,
                                                   layer_level_id = layer_level_id,
                                                   subcomponent_index = subcomponent_index,
                                                   atlas_image = atlas_image,
                                                   tile_size_px = tile_size_px,
                                                   atlas_coordinates_px= atlas_coordinates_px,
                                                   world_position_tile = world_position_tile,
                                                   world_coordinates_px= world_coordinates_px,
                                                   ground_position_px = ground_position_px)
        self._animated_tile_data = animated_tile_data

        #initialize the animation
        self._frame_timer = 0
        self._time_scaling_factor = 1.0
        self._current_frame_index = 0
        self._numb_frames = self._animated_tile_data.getNumbFrames()
        self._current_frame_duration = self._animated_tile_data.getDuration(self._current_frame_index)
        self._atlas_coordinates_px = self._animated_tile_data.getImageCoordinates(self._current_frame_index)
        #We don't need to do the frame calculation on every update, only when we are going to provide the graphic data
        #Just track how many updates we have had since the last display, then multiply by MS_PER_UPDATE
        self._numb_updates = 0

    #For animated tiles, we need to check if we are updating the frame
    #Frame is updated by updating the atlast coordinates
    def calculateCoordinates(self,
                             camera_offset, #[int, int]
                             lag_normalized): #float [0,1)  - We don't really care about lag for an animated tile
        #Timer incremented based on number of updates since last time
        self._frame_timer += int((TIMING_PARAM.MS_PER_UPDATE*self._numb_updates) * self._time_scaling_factor)
        self._numb_updates = 0
        if self._frame_timer >= self._current_frame_duration: #update the frame
            self._current_frame_index +=1
            if self._current_frame_index >= self._numb_frames:
                self._current_frame_index = 0
            self._atlas_coordinates_px = self._animated_tile_data.getImageCoordinates(self._current_frame_index)
            self._current_frame_duration = self._animated_tile_data.getDuration(self._current_frame_index)
            self._frame_timer = 0

        #This portion is identical to the TileInstance.calculateCoordinates call
        self._current_position_px = (self._world_coordinates_px[0] - camera_offset[0],
                                     self._world_coordinates_px[1] - camera_offset[1],
                                     0) #we won't ever have a Z component for a tile

    #We don't always flip the graphics (several updates per render call)
    #We just keep track of how many times we have updated since the last render
    def update(self):
        self._numb_updates+=1

class AtlasComponent:
    def __init__(self,
                 tile_size_px, #[int,int]
                 tile_count, #int
                 numb_columns, #int
                 first_gid, #int - gid is the unique ID of each tile in all atlases in a scene
                 max_gid, #int - by knowing the min/max gid, we can check if a tile is in this atlas
                 floating_tile_gids, #[int]
                 image, #pygame.image
                 animated_tile_datas): #[AnimatedTileData]
        self.tile_size_px = tile_size_px
        self.tile_count = tile_count
        self.numb_columns = numb_columns
        self.first_gid = first_gid
        self.max_gid = max_gid
        self.floating_tile_gids = floating_tile_gids
        self.image = image
        self.animated_tile_datas = animated_tile_datas

#Tile instances will not be wrapped as pointers - thus any changes must be made TO the tile instance, not
#by creating or replacing the instance.  If you change or replace this instance, the scenelayer will not
#get the updated instance
class TilemapComponent(SceneComponent):
    def __init__(self,
                 scene_element_id, #int
                 layer_element_id, #int
                 layer_level_id,  #int
                 static_tiles, #{(x,y) : TileInstance}
                 animated_tiles): #{(x,y) : AnimatedTileInstance}
        super(TilemapComponent, self).__init__(scene_element_id = scene_element_id,
                                               layer_element_id = layer_element_id,
                                               layer_level_id = layer_level_id)

        self._static_tiles = static_tiles
        self._animated_tiles = animated_tiles
        self._tile_instances = list() #- will change to TUPLE

    #We need to call this before we will have our list of tiles ready to send to the render_layer
    def initialize(self):
        #We create a list of renderables which will be requested by the render_layer
        #While we have seperate animated and static tiles stored, we send them as one big bath
        for static_tile in self._static_tiles.values():
            self._tile_instances.append(static_tile)
        for animated_tile in self._animated_tiles.values():
            self._tile_instances.append(animated_tile)

        #For efficient update() calls, we want a listified version of animated_tiles
 #       self._animated_tile_list = list(self._animated_tiles.values()) #TODO - DEBUG

        #Now we need to sort the Animated/Static tiles by their Y coordinates
        #Tilemaps aren't sorted on render so we need to do it once on create
        for i in range(1, len(self._tile_instances)):
            key = self._tile_instances[i]
            j = i - 1
            #Sort on the Y position of the renderable
            while j >= 0 and \
                    key.getGroundPositionPx()[1] < self._tile_instances[j].getGroundPositionPx()[1]:
                self._tile_instances[j+1] = self._tile_instances[j]
                j -= 1
            self._tile_instances[j+1] = key
        self._tile_instances = tuple(self._tile_instances)

    def getRenderables(self):
        return self._tile_instances

    def update(self):
        #for animated_tile in self._animated_tile_list:
        for animated_tile in self._animated_tiles.values():
            animated_tile.update()

class TilemapComponentSystem(SceneComponentSystem):
    def __init__(self):
        super(TilemapComponentSystem, self).__init__()
        self._tilemap_components = dict()  #{int : component}: keyed on the element_ids
        #all of the scenes contain their own set of atlases.  If multiple loaded scenes use the same atlas, the data
        #is partially duplicated, but the image will only be loaded one time (the rest of the data is minimal)
        self._atlas_components = dict() #{int : list()} : keyed on gamescene_resource_id, listed in index order of atlast for that scene

    def update(self):
        for tilemap_component in self._tilemap_components.values():
            tilemap_component.update()

    def getSceneComponents(self,
                           component_element_id): #int
        try:
            return self._tilemap_components[component_element_id].getRenderables()
        except:
            return list() #empty set if there is no element with this id

    #note that the tile_id in the tilemap is +1 relative to the ID in the atlas
    #this is because the atlas indexes tiles from 0, but on the tilemap 0 is for no tile
    #this is from Tiled (.tmx foramat).  I would have gone with -1 for no tile....
    def createComponent(self,
                        scene_element_id,
                        layer_element_id,
                        layer_level_id,
                        resource_data):

        #After all tile isntances are created, iterate through floating tiles and update ground pos
        def setTileGroundHeight(floating_tiles, #[TileInstance] #TODO - TEST THIS FUNCTION
                                static_tiles, #{(int,int) : TileInstance}
                                animated_tiles): #{(int,int) : TileInstance}
            max_y = resource_data.size_tiles[1] - 1 #There is no tile position below this
            tile_size_px = resource_data.tile_size_px
            for floating_tile in floating_tiles:
                current_x = floating_tile.getWorldPositionTile()[0] #The tile's x position
                current_y = floating_tile.getWorldPositionTile()[1] #The tile's y position, will be incremented
                #we are looking for a non_floating tile below this one (in y position)
                #Once we find it, we will set the Y position of this tile to that one.
                while current_y < max_y:
                    current_y += 1
                    static_tile = static_tiles.get((current_x, current_y)) #See if a tile exists at this position
                    if static_tile is not None and not static_tile.isFloating(): #If it exists and isn't floating
                        break #This tile is not floating and is below our floating tile
                    animated_tile = animated_tiles.get((current_x, current_y))
                    if animated_tile is not None and not animated_tile.isFloating(): #Check the animated tiles
                        break #This tile is not floating and is below our floating tile
                current_ground_position = floating_tile.getGroundPositionPx()
                floating_tile.setGroundPositionPx([current_ground_position[0],
                                                   (current_y+1)*tile_size_px[1], #The plus 1 is to get the bottom of the tile
                                                   0])

        gamescene_resource_id = resource_data.gamescene_resource_id #need this to find corresponding atlas's
        atlas_components = self._atlas_components[gamescene_resource_id]
        subcomponent_index = 0 #will increment for every tile
        static_tiles = dict()
        animated_tiles = dict()
        #This is a temporary list to track the floating tiles.  After all tiles are created, iterate
        #through this list and update the floating_tile with it's correct height
        floating_tiles = list()
        #build the component first so we can pass the ref to the subcomponents
        tilemap_component = TilemapComponent(scene_element_id = scene_element_id,
                                             layer_element_id = layer_element_id,
                                             layer_level_id = layer_level_id,
                                             static_tiles = static_tiles,
                                             animated_tiles = animated_tiles)
        current_tile_x = 0 #we start on col 0
        current_tile_y = 0 #we start on row 0
        for tile_id_row in resource_data.tile_id_lists:
            current_tile_x = 0
            for tile_id in tile_id_row:
                if tile_id>0: #0 means no tile, won't even create that object
                    #Based on the tile_id, we need to find which atlas it is from
                    atlas_index = 0
                    atlas_found = False
                    while not atlas_found:
                        if atlas_components[atlas_index].first_gid <= tile_id <= atlas_components[atlas_index].max_gid:
                            atlas_found = True
                        else:
                            atlas_index+=1
                    atlas = atlas_components[atlas_index] #shortcut to the current atlas we need
                    world_x = atlas.tile_size_px[0] * current_tile_x
                    world_y = atlas.tile_size_px[1] * current_tile_y
                    #See if this is an animated or static tile
                    if atlas.animated_tile_datas.get(tile_id-atlas.first_gid) is not None:
                        animated_tile = AnimatedTileInstance(parent_component = tilemap_component,  #for the whole tilemap
                                                             component_element_id=scene_element_id,  # for the whole tilemap
                                                             layer_level_id = layer_level_id,
                                                             subcomponent_index = subcomponent_index,
                                                             atlas_image = atlas.image,
                                                             tile_size_px = atlas.tile_size_px,
                                                             atlas_coordinates_px= [0, 0],  #is initialized in constructor
                                                             world_position_tile = (current_tile_x, current_tile_y),
                                                             world_coordinates_px = (world_x, world_y, 0),
                                                             ground_position_px =(world_x,
                                                                                  world_y + resource_data.tile_size_px[1], #bottom of the tile
                                                                                  0), #if this tile is floating, that will change
                                                             animated_tile_data = atlas.animated_tile_datas[tile_id-atlas.first_gid])
                        animated_tiles[(current_tile_x, current_tile_y)]= animated_tile
                        if atlas.floating_tile_gids.get(tile_id-atlas.first_gid) is not None:
                            floating_tiles.append(animated_tile)
                            animated_tile.setFloating(True)
                    else:
                        #by subtracting the atlas.first_gid val, we align the tile_id in the tilemap
                        #with the actual tile_index on the atlas
                        atlas_coordinates = convertGidToXY(tile_gid = tile_id-atlas.first_gid,
                                                           numb_columns = atlas.numb_columns,
                                                           tile_size_px =atlas.tile_size_px)
                        static_tile = TileInstance(parent_component = tilemap_component,
                                                   component_element_id=scene_element_id,
                                                   layer_level_id = layer_level_id,
                                                   subcomponent_index = subcomponent_index,
                                                   atlas_image = atlas.image,
                                                   tile_size_px = atlas.tile_size_px,
                                                   atlas_coordinates_px= atlas_coordinates,
                                                   world_position_tile=(current_tile_x, current_tile_y),
                                                   world_coordinates_px=(world_x, world_y, 0),
                                                   ground_position_px=(world_x,
                                                                       world_y + resource_data.tile_size_px[1],
                                                                       0)) #if this tile is floating, that will change
                        static_tiles[(current_tile_x, current_tile_y)] = static_tile
                        if atlas.floating_tile_gids.get(tile_id-atlas.first_gid) is not None:
                            floating_tiles.append(static_tile)
                            static_tile.setFloating(True)
                    subcomponent_index +=1
                current_tile_x +=1
            assert(current_tile_x == resource_data.size_tiles[0])
            current_tile_y +=1
        assert(current_tile_y == resource_data.size_tiles[1])
        setTileGroundHeight(floating_tiles, static_tiles, animated_tiles)
        tilemap_component.initialize()
        self._tilemap_components[scene_element_id] = tilemap_component
        return tilemap_component


    def createAtlas(self,
                    gamescene_resource_id,
                    atlas_resource_data):
        #If we don't have an atlas list yet for this scene_id, create it
        if self._atlas_components.get(gamescene_resource_id) is None:
            self._atlas_components[gamescene_resource_id] = list()
        #We should only add each atlas once, in order.
        #The gamescene_resource_id is the index, so we would expect it to be the same as the length of this array
        assert(atlas_resource_data.atlas_index == len(self._atlas_components[gamescene_resource_id]))
        first_gid = atlas_resource_data.first_gid
        max_gid = first_gid + atlas_resource_data.tile_count - 1
        animated_tile_datas = dict()

        #Some of the gids in the atlas are animated.  We have a dict to reference each animation set
        #For each set, use the gid as the key, and then translate XY position for each tile in the sequence
        for gid, animated_tile_resource_data in atlas_resource_data.animated_tile_resource_datas.items():
            tile_coordinates = list()
            numb_frames = 0
            for tile_gid in animated_tile_resource_data.tile_gids:
                tile_coordinates.append(convertGidToXY(tile_gid = tile_gid,
                                                       numb_columns = atlas_resource_data.numb_columns,
                                                       tile_size_px = atlas_resource_data.tile_size_px))
                numb_frames+=1
            animated_tile_datas[gid] = AnimatedTileData(tile_coordinates = tile_coordinates,
                                                        tile_size_px=atlas_resource_data.tile_size_px,
                                                        durations = animated_tile_resource_data.durations,
                                                        numb_frames = numb_frames)

        atlas_component = AtlasComponent(tile_size_px = atlas_resource_data.tile_size_px,
                                         tile_count = atlas_resource_data.tile_count,
                                         numb_columns = atlas_resource_data.numb_columns,
                                         first_gid = first_gid,
                                         max_gid = max_gid,
                                         floating_tile_gids = atlas_resource_data.floating_tile_gids,
                                         image = atlas_resource_data.image,
                                         animated_tile_datas = animated_tile_datas)
        self._atlas_components[gamescene_resource_id].append(atlas_component)

#based on the gid of a tile in an atlas, get it's XY origin in that atlas
    #Note: Because Tiled (tmx format) uses a stupid system, we get ID's on the atlas with 0 being the first tile
    #But the data in the tilemap makes 0 as a No_tile spot, which means that all of the data on the tilemap
    #is actually plus 1 from the ID in the atlas!  Be careful!
def convertGidToXY(tile_gid, #int
                   numb_columns, #int
                   tile_size_px): #[int,int]
    tile_row = tile_gid // numb_columns
    tile_column = tile_gid - (tile_row * numb_columns)
    return [tile_column * tile_size_px[0],  tile_row * tile_size_px[1]]













