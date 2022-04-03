import parameters as PRAM

# Image that can be used as layer of background or foreground.  Can be set to tile or scroll, and
# sections that are visible relative to the game level can be chosen
#
# @param path: directory of image
# @param image: filename of image
# @param imageSize: size in pixels of image [x,y]
# @param visibleSections: 2d array: each array is a box [left edge, right edge, top edge, bottom edge]
# @param scrolling: [[Xmultiplier, Xdivisor], [Xmultiplier, Xdivisor]]
# @param: alpha: does the image contain alpha information (e.g. invisiible pixels)
#
# Scroll speed can be calculated to perfectly scroll the level in the level editor, or user chosen. Formula to scroll the level is
#
# X direction:
# numerator: levelSize - displaywidth
# denomonator: imageSize - displaywidth
# numerator/denomonator = scroll speed in X direction to scroll the image over the entire level
#
# Y direction is same using Y params and displayheight
#
# NOTE if imageSize=displayWidth than set scroll speed to 0
#
# The above calculates the divisor.  Multiplier makes the image scroll faster then the level, so this must be user chosen.
# If user desires a 1.4 scroll speed, choose a multiplier of 14 and divisor of 10.

##DEV
# isMotion = True means the panorama scrolls in X/Y direction as screen stays still
# motionX_pxs - Pixels per second (positive/negative determines direction) in X direction
# movementY_pxs - Pixels per second (positive/negative determines direction) in Y direction

##DEV
# isAnimated = True means the panorama is animated
# animated_ips = number of images per second
# animated panorama filepath is to a directory of numbered pictures [0.<extension>, 1.<extension>, etc]
# engine will go through all images in order at designated fps (frames per second)

class PanoramicImage:
    def __init__(self, 
                 filePath = '', 
                 pxSize = (10,10),
                 visibleSections = ([0,200,0,200],[200,500,200,500]),
                 scrolling = ([1,1],[1,1]),
                 alpha = False,
                 layer= 0,
                 isMotion_X = False,
                 isMotion_Y = False,
                 motionX_pxs = 0,
                 motionY_pxs = 0,
                 isAnimated = False,
                 animated_fps = 0,
                 numbImages = 1,
                 imageType = 'png'):
        self.filePath = filePath
        self.pxSize = pxSize
        self.visibleSections = visibleSections
        self.scrolling = scrolling
        self.alpha = alpha
        self.layer = layer
        self.isMotion_X = isMotion_X
        self.isMotion_Y = isMotion_Y
        self.motionX_pxs = motionX_pxs
        self.motionY_pxs = motionY_pxs
        self.isAnimated = isAnimated
        self.animated_fps = animated_fps
        self.numbImages = numbImages
        self.imageType = imageType

        #explicit declaration of class fields
        self.image = None # the image date

        self.motion_x_multiplier = motionX_pxs/PRAM.GAME_FPS #calculated by the Renderer on level load based on Game FPS
        self.motion_y_multiplier = motionY_pxs/PRAM.GAME_FPS
        self.framesPerImage = round(PRAM.GAME_FPS / self.animated_fps, 2)
        self.imageIndex = 0 #tracks which image to display, if animated

        self.motionOffset_X = 0 #used to determine if re-render needed on render changed call
        self.motionOffset_Y = 0

    def updateFrameIndex(self):
        self.imageIndex = (self.imageIndex + 1) % self.numbImages

# Class to contain data for a tilemap
# The tiles are stored in 1 image file. To blit a tile correctly, use tiles index -
# - and calculate based on tilesize and tiles per row
# A tile index 0 is blank (nothing blitted)
# If the tilemap contains animated tiles, the animated tiles begin at the highest index.  All frames are stored
# sequentially in the tilemap image.  The tiles index will always reference the first tile in an animated group
# Go througn the animated tiles sequence based on framecount
# Must start at X = 0 for first animated tile (even if requires some blank tiles in the row above),
# Although upper and lower stored in same DB row, this continer holds just one
# Does not hold the borders info
# animatedOffsets dict stores reference to first animated tile in a series by coordinate pair, which loads a tuple
# of coordinate pairs which are the animated tile sequence
class Tilemap:
    def __init__(self,
                 filePath = '', #location of image to load
                 tileSize_px = 48,
                 height_tiles = 3,
                 width_tiles = 3,
                 tiles = ((0,0,0),(0,0,0),(0,0,0),), #this maps the location on the image to load based on tilesize
                 mapType = 'lower', #lower or upper tilemap
                 alpha = False, #True if contains alpha data
                 isAnimated = False, #if animated, some tiles contain multiple frames
                 animatedIndex = 500, #the tiles below this y value are in the animated group
                 numbFrames = 1, #how many frames there are in the animation, ie how many tiles in an animated group
                 fps = 1): #how fast the animation should play
        self.filePath = filePath
        self.height_tiles = height_tiles
        self.width_tiles = width_tiles
        self.tileSize_px = tileSize_px
        self.tiles = tiles
        self.mapType = mapType
        self.alpha = alpha
        self.isAnimated = isAnimated
        self.animatedIndex = animatedIndex #passed in as a tile index, then re-calculated to the Y pixel value - is index of first animated tile
        self.numbFrames = numbFrames #number of frames for animates tiles
        self.fps = fps

        #explicit declaration of class fields
        self.image = None
        # if animated, the number of frames per each image flip, calculated in renderer leve load
        self.framesPerImage = round(PRAM.GAME_FPS/fps,2)
        self.frameIndex = 0 #tracks which frame to display, if tile is animated
        self.animatedOffsets = {} #series of offsets for each animated tile group

        # any tile with a y value greater is part of an animated group
        if self.isAnimated:
            self.animatedDivide_px = ( (self.animatedIndex-1) // PRAM.TILEMAP_MAX_WIDTH) * PRAM.TILESIZE
        else:
            self.animatedDivide_px = (height_tiles*width_tiles)*PRAM.TILESIZE #y value never will be greater
        #reformats the tile indexes to pixel coordinates, calculates animated offsets, comresses to tuple
        self.tilemapIndexToCoord()
        self.makeTileListTuple()

    def updateFrameIndex(self):
        self.frameIndex = (self.frameIndex + 1) % self.numbFrames

    # takes a tile list of integers, corresponding to a tilemap position
    # returns the list as a tuple of pixel coordinate pairs
    def tilemapIndexToCoord(self):
        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[i])):
                index = self.tiles[i][j] - 1  # offset to start tilemap at 0 (first square is 1)

                if index < 0:  # blank tile:
                    self.tiles[i][j] = (-1, -1)  # -1 is code for blank

                elif self.isAnimated and index >= self.animatedIndex - 1: #calculate the offset of each tile in the sequence
                    y_reference = index // PRAM.TILEMAP_MAX_WIDTH
                    x_reference = index - (y_reference * PRAM.TILEMAP_MAX_WIDTH)
                    y_reference *= PRAM.TILESIZE
                    x_reference *= PRAM.TILESIZE
                    self.tiles[i][j] = (x_reference, y_reference) #update the tile to coordinate pair
                    if self.animatedOffsets.get((x_reference, y_reference)) is None: #lookup the animated coordinates based on first tile
                        offsets = []
                        for k in range(self.numbFrames):
                            y_tile = (index+k) // PRAM.TILEMAP_MAX_WIDTH
                            x_tile = (index+k) - (y_tile * PRAM.TILEMAP_MAX_WIDTH)
                            offsets.append((x_tile * PRAM.TILESIZE, y_tile * PRAM.TILESIZE))
                        offsets = tuple(offsets)
                        self.animatedOffsets[(x_reference, y_reference)] = offsets #this is a sequence of tiles to iterate through

                else: #calcu;ate the pixel offset of the tile
                    y_tile = index // PRAM.TILEMAP_MAX_WIDTH
                    x_tile = index - (y_tile * PRAM.TILEMAP_MAX_WIDTH)
                    self.tiles[i][j] = (x_tile * PRAM.TILESIZE, y_tile * PRAM.TILESIZE)

    #compreds the tile lists into tuples for efficiency
    def makeTileListTuple(self):
        for i in range(len(self.tiles)):
            self.tiles[i] = tuple(self.tiles[i])
        self.tiles = tuple(self.tiles)