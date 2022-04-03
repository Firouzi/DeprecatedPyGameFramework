from actors import SimpleBox, CharacterSprite, AnimationAccessory, AnimationPosition, AnimationState, SpriteAnimation, AccessoryPosition
import pygame
import parameters as PRAM

#renderQ and visibleSection indexes
LEFT_EDGE = 0
RIGHT_EDGE = 1
TOP_EDGE = 2
BOTTOM_EDGE = 3

LEFT_ANIM = 0
RIGHT_ANIM = 1
DOWN_ANIM = 2
UP_ANIM = 3

FROZE_ANIM = 0
FORWARD_ANIM = 1
REVERSE_ANIM = 2

#renderMethods list populated by game depending on the needs of the currently loaded level/menu
class Renderer:
    def __init__(self, screen):
        self.screen = screen
        
        #explicit declaration of class fields
        self.camera = None
        self.cameraTile= (0,0)
        self.cameraOffset = (0,0)
        self.cameraPosition = (0,0)
        
        self.levelData = None
        self.backgrounds = []
        self.foregrounds = []
        self.actors = []
        self.actorDict = None

        #for rendering changed tiles, keeps track of rendered tiles
        #indexed by their (x,y) coordinate pair
        self.renderedLowerTiles = {} 
        self.renderedUpperTiles = {} 

        self.lowerTileMap = None # Object holds tile mapping and image data
        self.upperTileMap = None # Object holds tile mapping and image data
        self.animatedPanorama = False

        self.isRenderAll = True #if true, will render the entire screen
        self.renderQueue = []
        self.framecount = 0 #a running count of frame ticks to animate images

    #this will just render game levels - create a seperate method for menus, and perhaps cutscenes
    def render(self):
        self.cameraTile= self.camera.tile
        self.cameraOffset = self.camera.offset
        self.cameraPosition = self.camera.position

        if  self.camera.moveFlag:# or self.animatedPanorama:
            self.isRenderAll = True

        if self.lowerTileMap is not None: #quick hack to make sure a level is loaded

            self.updateAnimatedIndex() #update any frame indexes for animated tiles

            if self.isRenderAll: #render the entire screen all layers
                self.renderAllPanorama(BG = True)
                self.renderAllTiles(lower = True)
                self.renderAllActors()
                self.renderAllTiles(lower = False)
                self.renderAllPanorama(BG = False)

            else: #render all layers for each changed section, based on render Q and render Tiles
                self.renderChangedPanorama(BG = True)
                self.renderChangedTiles(lower = True)
                self.renderChangedActors()
                self.renderChangedTiles(lower = False)
                self.renderChangedPanorama(BG = False)

            self.renderQueue.clear()
            self.renderedLowerTiles.clear()
            self.renderedUpperTiles.clear()
            self.camera.moveFlag = False
            self.isRenderAll = False

        self.framecount+=1

    #updates the index of any animated images
    def updateAnimatedIndex(self): #TODO - move some of this logic into the classes (eg updating framecount)
        if self.lowerTileMap.isAnimated:
            if int(self.framecount % self.lowerTileMap.framesPerImage) == 0:  # time to change the pic
                self.lowerTileMap.updateFrameIndex()
                if not self.isRenderAll: #if everything is being rendered, don't need to add to changed q
                    self.addRenderBoxes_AnimatedLowerTiles()

        if self.upperTileMap.isAnimated:
            if int(self.framecount % self.upperTileMap.framesPerImage) == 0:  # time to change the pic
                self.upperTileMap.updateFrameIndex()
                if not self.isRenderAll:
                    self.addRenderBoxes_AnimatedUpperTiles()

        for bg in self.backgrounds:
            addRenderBox = False
            if bg.isAnimated:
                if int(self.framecount%bg.framesPerImage)==0: #time to change the pic
                    bg.updateFrameIndex()
                    addRenderBox = True
            if bg.isMotion_X:
                motionOffset = int(bg.motion_x_multiplier * self.framecount)
                if motionOffset != bg.motionOffset_X: #panorama needs to move
                    bg.motionOffset_X = motionOffset
                    addRenderBox = True #if panorama needs to scroll, re-render visibile sections
            if bg.isMotion_Y:
                motionOffset = int(bg.motion_y_multiplier * self.framecount)
                if motionOffset != bg.motionOffset_Y:
                    bg.motionOffset_Y = motionOffset
                    addRenderBox = True
            if addRenderBox and not self.isRenderAll:
                self.addRenderBox_changedPanorama(bg)

        for fg in self.foregrounds:
            addRenderBox = False
            if fg.isAnimated:
                if int(self.framecount%fg.framesPerImage)==0: #time to change the pic
                    fg.updateFrameIndex()
                    addRenderBox = True
            if fg.isMotion_X:
                motionOffset = int(fg.motion_x_multiplier * self.framecount)
                if motionOffset != fg.motionOffset_X: #panorama needs to move
                    fg.motionOffset_X = motionOffset
                    addRenderBox = True #if panorama needs to scroll, re-render visibile sections
            if fg.isMotion_Y:
                motionOffset = int(fg.motion_y_multiplier * self.framecount)
                if motionOffset != fg.motionOffset_Y:
                    fg.motionOffset_Y = motionOffset
                    addRenderBox = True
            if addRenderBox and not self.isRenderAll:
                self.addRenderBox_changedPanorama(fg)

        for actor in self.actors: #TODO - check if onscreen?
            actor.characterSprite.updateAnimatedIndex() #better pattern to avoid violating demeter, etc?

    def renderAllTiles(self, lower = True):
        if lower:
            tilemap = self.lowerTileMap
        else:
            tilemap = self.upperTileMap
        tiles = tilemap.tiles #for efficiency, quick reference to ptr
        image = tilemap.image
        animatedDivide_px = tilemap.animatedDivide_px
        animatedOffsets = tilemap.animatedOffsets

        if tilemap.isAnimated:
            frameIndex = tilemap.frameIndex
        else:
            frameIndex = 0

        for y in range(PRAM.DISPLAY_TILE_HEIGHT):
            yOffset = y * PRAM.TILESIZE - self.cameraOffset[1]
            for x in range(PRAM.DISPLAY_TILE_WIDTH):
                tile = tiles[y + self.cameraTile[1]][x + self.cameraTile[0]]
                if tile[0] != -1: #-1 is blank
                    xOffset = x* PRAM.TILESIZE - self.cameraOffset[0]
                    if tile[1] >= animatedDivide_px:
                        tile = animatedOffsets.get((tile[0],tile[1]))[frameIndex]
                    self.screen.blit(image,
                                     (xOffset, yOffset), #screen position
                                     (tile[0], #tileMap x crop position
                                      tile[1], #tileMap y crop position
                                     PRAM.TILESIZE, #tilemap  width
                                     PRAM.TILESIZE)) #tilemap height

    def renderChangedTiles(self, lower = True):
        if lower:
            tilemap = self.lowerTileMap
            renderedTiles = self.renderedLowerTiles
        else:
            tilemap = self.upperTileMap
            renderedTiles = self.renderedUpperTiles
        tiles = tilemap.tiles
        image = tilemap.image
        animatedDivide_px = tilemap.animatedDivide_px
        animatedOffsets = tilemap.animatedOffsets

        if tilemap.isAnimated:
            frameIndex = tilemap.frameIndex
        else:
            frameIndex = 0

        for changedTile, isRendered in renderedTiles.items():
            if not isRendered:
                tile = tiles[changedTile[0]][changedTile[1]] #the tilemap image location
                if tile[1] >= animatedDivide_px:
                    tile = animatedOffsets.get((tile[0], tile[1]))[frameIndex]
                self.screen.blit(image,
                                 ((changedTile[1]  - self.cameraTile[0]) * PRAM.TILESIZE  - self.cameraOffset[0], #x screen position
                                  (changedTile[0] - self.cameraTile[1]) * PRAM.TILESIZE  - self.cameraOffset[1]), #y screen position
                                 (tile[0], #tilemap image coordinates
                                  tile[1],
                                 PRAM.TILESIZE,
                                 PRAM.TILESIZE)) #blit one tile

                renderedTiles[(changedTile[0],changedTile[1])] = True

    def renderAllPanorama(self, BG = True): #if BG render backgrounds, else foregrounds
        screenOffset = (self.cameraTile[0]*PRAM.TILESIZE + self.cameraOffset[0],
                        self.cameraTile[1]*PRAM.TILESIZE + self.cameraOffset[1])
        if BG:
            images = self.backgrounds
        else:
            images = self.foregrounds

        for fg in images:
            imageOffset = (((screenOffset[0]*fg.scrolling[0][0]//fg.scrolling[0][1])+fg.motionOffset_X)%fg.pxSize[1],
                           ((screenOffset[1]*fg.scrolling[1][0]//fg.scrolling[1][1])+fg.motionOffset_Y)%fg.pxSize[0])

            if fg.isAnimated:
                displayImage = fg.image[fg.imageIndex]
            else:
                displayImage = fg.image[0]

            for vs in fg.visibleSections: #vs = (left edge, right edge, top edge, bottom edge)
                
                #check if visible portion of background is on screen
                if (vs[0] < screenOffset[0] + PRAM.DISPLAY_WIDTH 
                    and vs[1]> screenOffset[0] 
                    and vs[2] < screenOffset[1] + PRAM.DISPLAY_HEIGHT 
                    and vs[3]> screenOffset[1]):
                    
                    #find boundaries of image
                    if vs[0] <= screenOffset[0]:
                        xOffset = 0
                    else:
                        xOffset = vs[0] - screenOffset[0]
                
                    if vs[2] <= screenOffset[1]:
                        yOffset = 0
                    else:
                        yOffset = vs[2]- screenOffset[1]

                    #calculate size of image square to blit  
                    xRange = vs[1] - screenOffset[0] - xOffset                      
                    if xRange + xOffset > PRAM.DISPLAY_WIDTH:
                        xRange = PRAM.DISPLAY_WIDTH - xOffset

                    yRange = vs[3] - screenOffset[1] - yOffset
                    if yRange + yOffset > PRAM.DISPLAY_HEIGHT:
                        yRange = PRAM.DISPLAY_HEIGHT - yOffset
                        
                    currentXrange = xRange #size of block of image to blit
                    currentYrange = yRange
                    currentScreenPos = [xOffset,yOffset] #absolute screen position to blit to
                    
                    currentCropX = (imageOffset[0] + xOffset)%fg.pxSize[1] #position of image to blit from
                    currentCropY = (imageOffset[1] + yOffset)%fg.pxSize[0]
                    keepGoing = True
                    shiftX = False
                    shiftY = False
                    
                    while keepGoing:
                        if currentCropX + currentXrange > fg.pxSize[1]:
                            currentXrange = fg.pxSize[1] - currentCropX
                            shiftX = True
                        if currentCropY + currentYrange > fg.pxSize[0]:
                            currentYrange = fg.pxSize[0] - currentCropY
                            shiftY = True

                        self.screen.blit(displayImage,
                                         currentScreenPos,
                                        (currentCropX, currentCropY, currentXrange, currentYrange)) 
                                                                 
                        #blit across the X direction first, then shift down the Y and reset the X  
                        if shiftX:
                            currentScreenPos = [currentScreenPos[0] + currentXrange, currentScreenPos[1]]
                            currentCropX = (currentCropX + currentXrange) % fg.pxSize[1]
                            currentXrange = xRange - currentXrange
                            shiftX = False
                        elif shiftY:
                            currentScreenPos = [xOffset, currentScreenPos[1] + currentYrange]
                            currentCropX = (imageOffset[0] + xOffset)%fg.pxSize[1]
                            currentXrange = xRange
                            currentCropY = (currentCropY + currentYrange) % fg.pxSize[0]
                            currentYrange = yRange - currentYrange                                                
                            shiftY = False    
                        else:
                            keepGoing = False #you have blitted the entire visible section

    def renderChangedPanorama(self, BG = True):
        if BG:
            images = self.backgrounds
        else:
            images = self.foregrounds

        screenBoundryLeft = self.screenBoundryLeft() #pixel 0 of screen is this map pixel
        screenBoundryTop = self.screenBoundryTop()

        for fg in images:

            if fg.isAnimated:
                displayImage = fg.image[fg.imageIndex]
            else:
                displayImage = fg.image[0]

            for box in self.renderQueue:
                for vs in fg.visibleSections:  #vs = (left edge, right edge, top edge, bottom edge)
                    visibleBox = self.getBoxOverlap(box, vs)
                    if visibleBox and self.isBoxOnScreen(visibleBox):
                        visibleBox = self.trimBoxToScreen(visibleBox)  #make sure we have a box within screen boundry

                        startScreenPos = [visibleBox[LEFT_EDGE] - screenBoundryLeft,  #relative coordinate of starting image position
                                          visibleBox[TOP_EDGE] - screenBoundryTop]

                        startCropX = (screenBoundryLeft
                                      * fg.scrolling[0][0]
                                      // fg.scrolling[0][1] 
                                      + startScreenPos[0]
                                      + fg.motionOffset_X)
                        startCropX = startCropX % fg.pxSize[1]  #where to start the crop from the image file

                        startCropY = (screenBoundryTop
                                      * fg.scrolling[1][0]
                                      // fg.scrolling[1][1] 
                                      + startScreenPos[1]
                                      + fg.motionOffset_Y)
                        startCropY = startCropY % fg.pxSize[0]

                        currentScreenPos = startScreenPos
                        currentCropX =  startCropX
                        currentCropY = startCropY

                        imageSizeX = visibleBox[RIGHT_EDGE] - visibleBox[LEFT_EDGE] #how much of the image do we need to blit
                        imageSizeY = visibleBox[BOTTOM_EDGE] - visibleBox[TOP_EDGE]

                        keepGoing = True
                        shiftX = False
                        shiftY = False

                        while keepGoing:  #check to see if you are at the boundries of the image, and need to tile it
                            if currentCropX + imageSizeX > fg.pxSize[1]:
                                imageSizeX = fg.pxSize[1] - currentCropX
                                shiftX = True #means we need to do at least 1 more blit to finish X direction
                            if currentCropY + imageSizeY > fg.pxSize[0]:
                                imageSizeY = fg.pxSize[0] - currentCropY
                                shiftY = True


                            self.screen.blit(displayImage,
                                             currentScreenPos,
                                            (currentCropX,  #image x
                                            currentCropY, #image y                                 
                                              imageSizeX, #image x width crop
                                              imageSizeY)) #image y height crop   

                            #blit across the X direction first, then shift down the Y and reset the X
                            if shiftX:
                                currentScreenPos = [currentScreenPos[0] + imageSizeX, currentScreenPos[1]]
                                currentCropX = (currentCropX + imageSizeX) % fg.pxSize[1]
                                imageSizeX = visibleBox[1] - visibleBox[0] - imageSizeX
                                shiftX = False
                            elif shiftY:
                                currentScreenPos = [startScreenPos[0], currentScreenPos[1] + imageSizeY]
                                currentCropX = startCropX
                                imageSizeX = visibleBox[1] - visibleBox[0]
                                currentCropY = (currentCropY + imageSizeY) % fg.pxSize[0]
                                imageSizeY = visibleBox[3] - visibleBox[2] - imageSizeY                                                
                                shiftY = False    
                            else:
                                keepGoing = False #you have blitted the entire visible section

    #TODO - calculate if the actor is onscreen
    def renderAllActors(self):
        for actor in self.actors:
            if type(actor) is SimpleBox and False: #TODO - debug, turning off to test sprite render
                pygame.draw.rect(self.screen, actor.color, 
                                 pygame.Rect(actor.position[0]+PRAM.BOX_FUDGE - self.cameraPosition[0], 
                                             actor.position[1] - self.cameraPosition[1], 
                                             actor.size[0] - PRAM.BOX_FUDGE*2, 
                                             actor.size[1]))

            else:
                image = actor.characterSprite.spriteAnimations[0].image #TODO, hardcoded, load the actual animation
                frame = actor.characterSprite.animationState.frameIndex
                position = actor.characterSprite.spriteAnimations[0].positions_px[actor.direction][frame]
                self.screen.blit(image,
                                 (actor.position[0]+PRAM.BOX_FUDGE - self.cameraPosition[0],
                                  actor.position[1] - self.cameraPosition[1]),  # screen position
                                 (position.start_x,  # tileMap x crop position
                                  position.start_y,  # tileMap y crop position
                                  position.width,  # tilemap  width
                                  position.height))  # tilemap height
            actor.changed = False
        return

    def renderChangedActors(self):
        for actor in self.actors:
            if actor.changed:
                if type(actor) is SimpleBox and False: #TODO - debug, turning off to test sprite render
                    pygame.draw.rect(self.screen, actor.color, 
                                     pygame.Rect(actor.position[0]+PRAM.BOX_FUDGE - self.cameraPosition[0], 
                                                 actor.position[1] - self.cameraPosition[1], 
                                                 actor.size[0] - PRAM.BOX_FUDGE*2, 
                                                 actor.size[1]))
                else:
                    image = actor.characterSprite.spriteAnimations[0].image  # TODO, hardcoded, load the actual animation
                    frame = actor.characterSprite.animationState.frameIndex
                    position = actor.characterSprite.spriteAnimations[0].positions_px[actor.direction][frame]  # get the 'Left', 1 images
                    self.screen.blit(image,
                                     (actor.position[0] + PRAM.BOX_FUDGE - self.cameraPosition[0],
                                      actor.position[1] - self.cameraPosition[1]),  # screen position
                                     (position.start_x,  # tileMap x crop position
                                      position.start_y,  # tileMap y crop position
                                      position.width,  # tilemap  width
                                      position.height))  # tilemap height
                actor.changed = False
        return

    #Based on start and end position, and actor size, add a bounding box to the renderQueue (in pixels)
    # for a section of the gameLevel that needs to be rendered on the render changes call
    # #also, adds to the tileRenderQueues any tiles in the box
    def addRenderBox_movedSprite(self, size, origin, destination, direction):
        if direction == PRAM.UP:
            minx = origin[0]
            miny = destination[1]
            maxx = destination[0] + size[0]
            maxy = origin[1] + size[1]
        elif direction == PRAM.DOWN:
            minx = origin[0]
            miny = origin[1]
            maxx = destination[0] + size[0]
            maxy = destination[1] + size[1]
        elif direction == PRAM.LEFT:
            minx = destination[0] 
            miny = origin[1]
            maxx = origin[0] + size[0]
            maxy = destination[1] + size[1]
        else: #right
            minx = origin[0]
            miny = origin[1]
            maxx = destination[0] + size[0]
            maxy = destination[1] + size[1]
        
        mapSizeX = self.levelData.size[1] * PRAM.TILESIZE #TODO save this as a levelData parameter?
        mapSizeY = self.levelData.size[0] * PRAM.TILESIZE
        
        #get the entire tile
        minx = minx - (minx % PRAM.TILESIZE)
        miny = miny - (miny % PRAM.TILESIZE)
        maxx = (maxx//PRAM.TILESIZE + 1)*PRAM.TILESIZE
        maxy = (maxy//PRAM.TILESIZE + 1)*PRAM.TILESIZE        
             
        if minx<0:
            minx = 0
        if miny<0:
            miny = 0
        if maxx > mapSizeX:
            maxx = mapSizeX
        if maxy > mapSizeY:
            maxy = mapSizeY

        renderBox = (minx, maxx, miny, maxy)
        self.renderQueue.append(renderBox) #for panorama rendering
        self.addChangedTilesFromRenderBox(renderBox) #for tile re-rendering

    def addChangedTilesFromRenderBox(self, renderBox):
        xRange = [renderBox[0]//PRAM.TILESIZE, renderBox[1]//PRAM.TILESIZE]
        yRange = [renderBox[2]//PRAM.TILESIZE, renderBox[3]//PRAM.TILESIZE]
        #don't check tiles beyond bound of level
        if xRange[1] > self.levelData.size[0]-1:
            xRange[1] = self.levelData.size[0]-1
        if yRange[1] > self.levelData.size[1]-1:
            yRange[1] = self.levelData.size[1]-1

        for x in range(xRange[0], xRange[1]):
            for y in range(yRange[0], yRange[1]):
                lowerTile = self.lowerTileMap.tiles[y][x]
                upperTile = self.upperTileMap.tiles[y][x]
                if self.renderedLowerTiles.get((y,x)) != True and lowerTile[0] != -1: #-1 is blank
                    self.renderedLowerTiles[(y,x)] = False
                if self.renderedUpperTiles.get((y,x)) != True and upperTile[0] != -1:
                    self.renderedUpperTiles[(y,x)] = False


    def addRenderBox_changedPanorama(self, panorama):
        screenOffset = (self.cameraTile[0]*PRAM.TILESIZE + self.cameraOffset[0],
                        self.cameraTile[1]*PRAM.TILESIZE + self.cameraOffset[1])

        for vs in panorama.visibleSections:  # vs = (left edge, right edge, top edge, bottom edge)
            # check if visible portion of background is on screen
            if (vs[0] < screenOffset[0] + PRAM.DISPLAY_WIDTH
                and vs[1] > screenOffset[0]
                and vs[2] < screenOffset[1] + PRAM.DISPLAY_HEIGHT
                and vs[3] > screenOffset[1]):

                box = list(vs)

                #trim the render box to the size of the screen
                if box[LEFT_EDGE] < self.screenBoundryLeft():
                    box[LEFT_EDGE] = self.screenBoundryLeft()
                if box[RIGHT_EDGE] > self.screenBoundryRight():
                    box[RIGHT_EDGE] = self.screenBoundryRight()
                if box[TOP_EDGE] < self.screenBoundryTop():
                    box[TOP_EDGE] = self.screenBoundryTop()
                if box[BOTTOM_EDGE] > self.screenBoundryBottom():
                    box[BOTTOM_EDGE] = self.screenBoundryBottom()

                #adjusts box to be on border of tiles, so that we render the tile and box boundry the same
                box[LEFT_EDGE] = box[LEFT_EDGE] - (box[LEFT_EDGE]%PRAM.TILESIZE)
                box[RIGHT_EDGE] = box[RIGHT_EDGE] + (PRAM.TILESIZE - (box[RIGHT_EDGE]%PRAM.TILESIZE))
                box[TOP_EDGE] = box[TOP_EDGE] - (box[TOP_EDGE]%PRAM.TILESIZE)
                box[BOTTOM_EDGE] = box[BOTTOM_EDGE] + (PRAM.TILESIZE - (box[BOTTOM_EDGE]%PRAM.TILESIZE))

                addedBoxes =self.addToRenderQueue(box)
                for addedBox in addedBoxes: #Add changed tiles only for sections actually added to the queue
                    self.addChangedTilesFromRenderBox(addedBox)

    def addRenderBoxes_AnimatedLowerTiles(self):
        lowerTiles = self.lowerTileMap.tiles #for efficiency, quick reference to ptr
        upperTiles = self.upperTileMap.tiles
        animatedDivide_px = self.lowerTileMap.animatedDivide_px
        cameraTile = self.cameraTile

        for y in range(PRAM.DISPLAY_TILE_HEIGHT):
            miny = (y + cameraTile[1]) * PRAM.TILESIZE
            maxy = miny + PRAM.TILESIZE
            tileOffset_y = y + cameraTile[1]
            for x in range(PRAM.DISPLAY_TILE_WIDTH):
                tileOffset_x = x + cameraTile[0]
                lowerTile = lowerTiles[tileOffset_y][tileOffset_x]
                if lowerTile[0] != -1:
                    if lowerTile[1] >= animatedDivide_px:
                        minx = (x + cameraTile[0])*PRAM.TILESIZE
                        maxx = minx+PRAM.TILESIZE
                        # self.renderQueue.append((minx, maxx, miny, maxy))  # for panorama rendering
                        self.addToRenderQueue((minx, maxx, miny, maxy))
                        self.renderedLowerTiles[(tileOffset_y, tileOffset_x)] = False
                        upperTile = upperTiles[tileOffset_y][tileOffset_x]
                        if upperTile[0] != -1:
                            self.renderedUpperTiles[(tileOffset_y, tileOffset_x)] = False #If we re-render lower, must also do upper


    def addRenderBoxes_AnimatedUpperTiles(self):
        lowerTiles = self.lowerTileMap.tiles #for efficiency, quick reference to ptr
        upperTiles = self.upperTileMap.tiles
        animatedDivide_px = self.upperTileMap.animatedDivide_px
        cameraTile = self.cameraTile

        for y in range(PRAM.DISPLAY_TILE_HEIGHT):
            miny = (y + cameraTile[1]) * PRAM.TILESIZE
            maxy = miny + PRAM.TILESIZE
            tileOffset_y = y + cameraTile[1]
            for x in range(PRAM.DISPLAY_TILE_WIDTH):
                tileOffset_x = x + cameraTile[0]
                upperTile = upperTiles[tileOffset_y][tileOffset_x]
                if upperTile[0] != -1:
                    if upperTile[1] >= animatedDivide_px:
                        minx = (x + cameraTile[0])*PRAM.TILESIZE
                        maxx = minx+PRAM.TILESIZE
                        self.addToRenderQueue((minx, maxx, miny, maxy))
                        self.renderedUpperTiles[(tileOffset_y, tileOffset_x)] = False
                        lowerTile = lowerTiles[tileOffset_y][tileOffset_x]
                        if lowerTile[0] != -1:
                            self.renderedLowerTiles[(tileOffset_y, tileOffset_x)] = False #If we re-render upper, must also do lower

    #Takes a candidate box, and adds it to the render Q, or a portion of it to the renderQ, if part of the box
    #is already in the render @
    def addToRenderQueue(self, candidateBox):
        if len(self.renderQueue) == 0:
            self.renderQueue.append(candidateBox)
            return [candidateBox] #so we always return a list
        else:
            newBoxes = self.boxesToAdd(candidateBox)
            self.renderQueue+=newBoxes
            return newBoxes #return what was added for a reference to use on adding tiles or other affected assets

    # Takes a candidateBox, and checks if it overlaps with a box already in the Q.
    # If not, return the box.  If it overlaps, recursively call this funciton
    # with the box split at the overlap points, returning any boxes that don't overlap a current box
    # will return an [] if the box is covered completely by the current Q, or a list of boxes which cover new area
    def boxesToAdd(self, candidateBox):
        newBoxes= []
        overlap = False
        for currentBox in self.renderQueue:

            #Check to see if we already include this section in the Q, if so return no boxes
            if candidateBox[RIGHT_EDGE] <= currentBox[RIGHT_EDGE] \
                    and candidateBox[LEFT_EDGE] >= currentBox[LEFT_EDGE] \
                    and candidateBox[TOP_EDGE] >= currentBox[TOP_EDGE] \
                    and candidateBox[BOTTOM_EDGE] <= currentBox[BOTTOM_EDGE]:
                return [] #This box is already covered by one of the boxes in the queue

            #see if the Y overlaps at all
            if candidateBox[BOTTOM_EDGE] > currentBox[TOP_EDGE] and candidateBox[TOP_EDGE] < currentBox[BOTTOM_EDGE]:

                # Overlaps on left side of current box
                if candidateBox[RIGHT_EDGE] > currentBox[LEFT_EDGE] > candidateBox[LEFT_EDGE]:
                    newBoxes += self.boxesToAdd([candidateBox[LEFT_EDGE],
                                                  currentBox[LEFT_EDGE],
                                                  candidateBox[TOP_EDGE],
                                                  candidateBox[BOTTOM_EDGE]]) #left half

                    newBoxes += self.boxesToAdd([currentBox[LEFT_EDGE],
                                                  candidateBox[RIGHT_EDGE],
                                                  candidateBox[TOP_EDGE],
                                                  candidateBox[BOTTOM_EDGE]]) #right half


                    overlap = True #if there is overlap, we know we don't return the original box
                    break

                # Overlaps on right side of current box
                elif candidateBox[LEFT_EDGE] < currentBox[RIGHT_EDGE] < candidateBox[RIGHT_EDGE]:
                    newBoxes += self.boxesToAdd([candidateBox[LEFT_EDGE],
                                                 currentBox[RIGHT_EDGE],
                                                 candidateBox[TOP_EDGE],
                                                 candidateBox[BOTTOM_EDGE]]) #left half

                    newBoxes += self.boxesToAdd([currentBox[RIGHT_EDGE],
                                                 candidateBox[RIGHT_EDGE],
                                                 candidateBox[TOP_EDGE],
                                                 candidateBox[BOTTOM_EDGE]]) #right half

                    overlap = True  # if there is overlap, we know we don't return the original box
                    break

                # Check if the candidate X is within the middle of the current, overlapping at top or bottom
                elif candidateBox[LEFT_EDGE] < currentBox[RIGHT_EDGE] and candidateBox[RIGHT_EDGE] > currentBox[LEFT_EDGE]:
                    # Overlaps on top side of current box
                    if candidateBox[TOP_EDGE] < currentBox[TOP_EDGE] < candidateBox[BOTTOM_EDGE]:
                        newBoxes += self.boxesToAdd([candidateBox[LEFT_EDGE],
                                                     candidateBox[RIGHT_EDGE],
                                                     candidateBox[TOP_EDGE],
                                                     currentBox[TOP_EDGE]]) #top half

                        newBoxes += self.boxesToAdd([candidateBox[LEFT_EDGE],
                                                     candidateBox[RIGHT_EDGE],
                                                     currentBox[TOP_EDGE],
                                                     candidateBox[BOTTOM_EDGE]]) #bottom half

                        overlap = True  # if there is overlap, we know we don't return the original box
                        break

                    # Overlaps on bottom side of current box
                    elif candidateBox[BOTTOM_EDGE] > currentBox[BOTTOM_EDGE] > candidateBox[TOP_EDGE]:
                        newBoxes += self.boxesToAdd([candidateBox[LEFT_EDGE],
                                                     candidateBox[RIGHT_EDGE],
                                                     candidateBox[TOP_EDGE],
                                                     currentBox[BOTTOM_EDGE]]) #top half

                        newBoxes += self.boxesToAdd([candidateBox[LEFT_EDGE],
                                                     candidateBox[RIGHT_EDGE],
                                                     currentBox[BOTTOM_EDGE],
                                                     candidateBox[BOTTOM_EDGE]]) #bottom half

                        overlap = True  # if there is overlap, we know we don't return the original box
                        break

        if overlap: #we split the candidate box up
            return newBoxes
        else:
            return [candidateBox] #there is no overlap with this box and any in the current render Q

    #given absolute box coords, trim to the boundries of the visible screen
    def trimBoxToScreen(self, box):
        trimmedBox = list(box)
        if box[LEFT_EDGE] < self.screenBoundryLeft():
            trimmedBox[LEFT_EDGE] = self.screenBoundryLeft()
        if box[RIGHT_EDGE] > self.screenBoundryRight():
            trimmedBox[RIGHT_EDGE] = self.screenBoundryRight()
        if box[TOP_EDGE] < self.screenBoundryTop():
            trimmedBox[TOP_EDGE] = self.screenBoundryTop()
        if box[BOTTOM_EDGE] > self.screenBoundryBottom():
            trimmedBox[BOTTOM_EDGE] = self.screenBoundryBottom()

        return trimmedBox

    #given 2boxes [left,right,top,bottom], return a box where they overlap, or an [] if no overlap
    def getBoxOverlap(self, box1, box2):
        # Check to see if any overlap at all
        if self.isBoxOverlap(box1, box2):
            overlap = [0, 0, 0, 0]

            if box1[LEFT_EDGE] > box2[LEFT_EDGE]:
                overlap[LEFT_EDGE] = box1[LEFT_EDGE]
            else:
                overlap[LEFT_EDGE] = box2[LEFT_EDGE]

            if box1[RIGHT_EDGE] < box2[RIGHT_EDGE]:
                overlap[RIGHT_EDGE] = box1[RIGHT_EDGE]
            else:
                overlap[RIGHT_EDGE] = box2[RIGHT_EDGE]

            if box1[TOP_EDGE] > box2[TOP_EDGE]:
                overlap[TOP_EDGE] = box1[TOP_EDGE]
            else:
                overlap[TOP_EDGE] = box2[TOP_EDGE]

            if box1[BOTTOM_EDGE] < box2[BOTTOM_EDGE]:
                overlap[BOTTOM_EDGE] = box1[BOTTOM_EDGE]
            else:
                overlap[BOTTOM_EDGE] = box2[BOTTOM_EDGE]

            return overlap

        else:
            return [] #no overlap

    #given a box of absolute coordinates, check if it is on the display surface
    def isBoxOnScreen(self,box):
        if box[LEFT_EDGE] < self.screenBoundryRight() and \
                        box[RIGHT_EDGE] > self.screenBoundryLeft() and \
                        box[TOP_EDGE] < self.screenBoundryBottom() and \
                        box[BOTTOM_EDGE] > self.screenBoundryTop():
            return True
        return False

    #return true if there is any overlap between two boxes
    def isBoxOverlap(self, box1, box2):
        if box1[LEFT_EDGE] < box2[RIGHT_EDGE] and \
                        box1[RIGHT_EDGE] > box2[LEFT_EDGE] and \
                        box1[TOP_EDGE] < box2[BOTTOM_EDGE] and \
                        box1[BOTTOM_EDGE] > box2[TOP_EDGE]:
            return True
        return False

    def screenBoundryLeft(self):
        return (self.cameraTile[0]*PRAM.TILESIZE) + self.cameraOffset[0]

    def screenBoundryRight(self):
        return (self.cameraTile[0] * PRAM.TILESIZE) + self.cameraOffset[0] + PRAM.DISPLAY_WIDTH

    def screenBoundryTop(self):
        return (self.cameraTile[1]*PRAM.TILESIZE) + self.cameraOffset[1]

    def screenBoundryBottom(self):
        return (self.cameraTile[1] * PRAM.TILESIZE) + self.cameraOffset[1] + PRAM.DISPLAY_HEIGHT

    def loadAssets(self, levelData):
        self.framecount = 0 #reset framecount
        self.levelData = levelData #TODO may not need this reference
        self.lowerTileMap = levelData.lowerTileMap
        self.upperTileMap = levelData.upperTileMap
        self.backgrounds = levelData.backgrounds
        self.foregrounds = levelData.foregrounds
        self.actors = levelData.actors # TODO - update the db schema

        #TODO temporary hardcoded load to test sprite animation
        #Start with a single frame
        acc1_head_filepath = 'C:\\Users\\Robert\\Repos\\PythonGameFramework\\source\\dir_image\\dir_sprites\\hero\\hero_acc1_head.png'

        walkLeftHeadPosition_0 = AccessoryPosition(0,96,48,96) #x, y ,width, height, relative_x, relative_y
        walkLeftHeadPosition_1 = AccessoryPosition(48,96,48,96) #x, y ,width, height, relative_x, relative_y
        walkLeftHeadPosition_2 = AccessoryPosition(96,96,48,96) #x, y ,width, height, relative_x, relative_y
        walkLeftHeadPosition_3 = AccessoryPosition(144,96,48,96) #x, y ,width, height, relative_x, relative_y

        walkRightHeadPosition_0 = AccessoryPosition(0,192,48,96) #x, y ,width, height, relative_x, relative_y
        walkRightHeadPosition_1 = AccessoryPosition(48,192,48,96) #x, y ,width, height, relative_x, relative_y
        walkRightHeadPosition_2 = AccessoryPosition(96,192,48,96) #x, y ,width, height, relative_x, relative_y
        walkRightHeadPosition_3 = AccessoryPosition(144,192,48,96) #x, y ,width, height, relative_x, relative_y

        walkUpHeadPosition_0 = AccessoryPosition(0,288,48,96) #x, y ,width, height, relative_x, relative_y
        walkUpHeadPosition_1 = AccessoryPosition(48,288,48,96) #x, y ,width, height, relative_x, relative_y
        walkUpHeadPosition_2 = AccessoryPosition(96,288,48,96) #x, y ,width, height, relative_x, relative_y
        walkUpHeadPosition_3 = AccessoryPosition(144,288,48,96) #x, y ,width, height, relative_x, relative_y

        walkDownHeadPosition_0 = AccessoryPosition(0,0,48,96) #x, y ,width, height, relative_x, relative_y
        walkDownHeadPosition_1 = AccessoryPosition(48,0,48,96) #x, y ,width, height, relative_x, relative_y
        walkDownHeadPosition_2 = AccessoryPosition(96,0,48,96) #x, y ,width, height, relative_x, relative_y
        walkDownHeadPosition_3 = AccessoryPosition(144,0,48,96) #x, y ,width, height, relative_x, relative_y

        headAccessory = AnimationAccessory(acc1_head_filepath,
                                           'Walk',
                                           'Walk_Helmet1',
                                           {LEFT_ANIM:[walkLeftHeadPosition_0, walkLeftHeadPosition_1, walkLeftHeadPosition_2, walkLeftHeadPosition_3],
                                            RIGHT_ANIM: [walkRightHeadPosition_0, walkRightHeadPosition_1, walkRightHeadPosition_2, walkRightHeadPosition_3],
                                            UP_ANIM: [walkUpHeadPosition_0, walkUpHeadPosition_1, walkUpHeadPosition_2, walkUpHeadPosition_3],
                                            DOWN_ANIM: [walkDownHeadPosition_0, walkDownHeadPosition_1, walkDownHeadPosition_2, walkDownHeadPosition_3]})

        acc2_feet_filepath = 'C:\\Users\\Robert\\Repos\\PythonGameFramework\\source\\dir_image\\dir_sprites\\hero\\hero_acc2_feet.png'
        feetAccessory = AnimationAccessory(acc2_feet_filepath,
                                           'Walk',
                                           'Walk_Feet1',
                                           {LEFT_ANIM:[walkLeftHeadPosition_0, walkLeftHeadPosition_1, walkLeftHeadPosition_2, walkLeftHeadPosition_3],
                                            RIGHT_ANIM: [walkRightHeadPosition_0, walkRightHeadPosition_1, walkRightHeadPosition_2, walkRightHeadPosition_3],
                                            UP_ANIM: [walkUpHeadPosition_0, walkUpHeadPosition_1, walkUpHeadPosition_2, walkUpHeadPosition_3],
                                            DOWN_ANIM: [walkDownHeadPosition_0, walkDownHeadPosition_1, walkDownHeadPosition_2, walkDownHeadPosition_3]})



        walkDownBodyPosition_0 = AccessoryPosition(0,0,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkDownBodyPosition_1 = AccessoryPosition(41,0,32,52, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkDownBodyPosition_2 = AccessoryPosition(80,0,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkDownBodyPosition_3 = AccessoryPosition(120,0,32,51, 6, 38) #x, y ,width, height, relative_x, relative_y

        walkLeftBodyPosition_0 = AccessoryPosition(0,52,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkLeftBodyPosition_1 = AccessoryPosition(41,52,32,52, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkLeftBodyPosition_2 = AccessoryPosition(80,52,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkLeftBodyPosition_3 = AccessoryPosition(120,52,32,51, 6, 38) #x, y ,width, height, relative_x, relative_y

        walkRightBodyPosition_0 = AccessoryPosition(0,106,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkRightBodyPosition_1 = AccessoryPosition(41,106,32,52, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkRightBodyPosition_2 = AccessoryPosition(80,106,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkRightBodyPosition_3 = AccessoryPosition(120,106,32,51, 6, 38) #x, y ,width, height, relative_x, relative_y

        walkUpBodyPosition_0 = AccessoryPosition(0,164,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkUpBodyPosition_1 = AccessoryPosition(40,164,35,52, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkUpBodyPosition_2 = AccessoryPosition(79,164,36,51, 6, 38) #x, y ,width, height, relative_x, relative_y
        walkUpBodyPosition_3 = AccessoryPosition(119,164,35,51, 6, 38) #x, y ,width, height, relative_x, relative_y

        acc2_body_filepath = 'C:\\Users\\Robert\\Repos\\PythonGameFramework\\source\\dir_image\\dir_sprites\\hero\\hero_acc3_body_compress.png'
        bodyAccessory = AnimationAccessory(acc2_body_filepath,
                                           'Walk',
                                           'Walk_Body1',
                                           {LEFT_ANIM:[walkLeftBodyPosition_0, walkLeftBodyPosition_1, walkLeftBodyPosition_2, walkLeftBodyPosition_3],
                                            RIGHT_ANIM: [walkRightBodyPosition_0, walkRightBodyPosition_1, walkRightBodyPosition_2, walkRightBodyPosition_3],
                                            UP_ANIM: [walkUpBodyPosition_0, walkUpBodyPosition_1, walkUpBodyPosition_2, walkUpBodyPosition_3],
                                            DOWN_ANIM: [walkDownBodyPosition_0, walkDownBodyPosition_1, walkDownBodyPosition_2, walkDownBodyPosition_3]})




        heroFilepath = 'C:\\Users\\Robert\\Repos\\PythonGameFramework\\source\\dir_image\\dir_sprites\\hero\\hero_walk_enlarge.png'

        walkLeftPosition_0 = AnimationPosition(0,96,48,96) #x, y ,width, height
        walkLeftPosition_1 = AnimationPosition(48,96,48,96) #x, y ,width, height
        walkLeftPosition_2 = AnimationPosition(96,96,48,96) #x, y ,width, height
        walkLeftPosition_3 = AnimationPosition(144,96,48,96) #x, y ,width, height

        walkRightPosition_0 = AnimationPosition(0,192,48,96) #x, y ,width, height
        walkRightPosition_1 = AnimationPosition(48,192,48,96) #x, y ,width, height
        walkRightPosition_2 = AnimationPosition(96,192,48,96) #x, y ,width, height
        walkRightPosition_3 = AnimationPosition(144,192,48,96) #x, y ,width, height

        walkUpPosition_0 = AnimationPosition(0,288,48,96) #x, y ,width, height
        walkUpPosition_1 = AnimationPosition(48,288,48,96) #x, y ,width, height
        walkUpPosition_2 = AnimationPosition(96,288,48,96) #x, y ,width, height
        walkUpPosition_3 = AnimationPosition(144,288,48,96) #x, y ,width, height

        walkDownPosition_0 = AnimationPosition(0,0,48,96) #x, y ,width, height
        walkDownPosition_1 = AnimationPosition(48,0,48,96) #x, y ,width, height
        walkDownPosition_2 = AnimationPosition(96,0,48,96) #x, y ,width, height
        walkDownPosition_3 = AnimationPosition(144,0,48,96) #x, y ,width, height

        walkAnimation = SpriteAnimation(heroFilepath,
                                        'Walk', #name
                                        4, #frames
                                        2, #fps
                                        {LEFT_ANIM:[walkLeftPosition_0, walkLeftPosition_1, walkLeftPosition_2, walkLeftPosition_3],
                                         RIGHT_ANIM: [walkRightPosition_0, walkRightPosition_1, walkRightPosition_2, walkRightPosition_3],
                                         UP_ANIM: [walkUpPosition_0, walkUpPosition_1, walkUpPosition_2, walkUpPosition_3],
                                         DOWN_ANIM: [walkDownPosition_0, walkDownPosition_1, walkDownPosition_2, walkDownPosition_3]},
                                        [feetAccessory,
                                         bodyAccessory,
                                         headAccessory])

        animationState = AnimationState(walkAnimation, #the current animation state
                                        LEFT_ANIM, #direction
                                        FORWARD_ANIM, #Animation Condition
                                        0, #frame index
                                        0, #frameCount
                                        100) #speed %

        characterSprite = CharacterSprite('Hero', [walkAnimation], animationState)

        self.actors[0].characterSprite = characterSprite

        for actor in self.actors: #TODO - this will need to be it's own method, for easy ability to reload sprites
            for animation in actor.characterSprite.spriteAnimations:
                baseImage = pygame.image.load(animation.filePath).convert_alpha()
                for accessory in animation.animationAccessories:
                    accessoryImage = pygame.image.load(accessory.filePath).convert_alpha()
                    for direction, positions in accessory.positions_px.items():
                        index = 0 #keep track of which frame we are on
                        for position in positions: #superimpose the accesory onto the base, frame by frame
                            baseImage.blit(accessoryImage, # where to copy to on the base image
                                             (animation.positions_px[direction][index].start_x + position.relative_x,
                                              animation.positions_px[direction][index].start_y + position.relative_y),
                                             (position.start_x,  # where to to start on the accessory map
                                              position.start_y,  #
                                              position.width,  # tilemap  width
                                              position.height))  # tilemap height
                            index +=1
                animation.image = baseImage #this is the completed image with accesories loaded




        self.animatedPanorama = False #if this is true, must always re-render entire screen every frame

        for background in self.backgrounds: #TODO - this will need to be it's own method, for easy ability to reload sprites
            if background.isAnimated:
                self.animatedPanorama = True
                background.image = loadAnimatedPanoramas(background)
            else:
                background.image = loadPanorama(background)
            if background.isMotion_X:
                self.animatedPanorama = True
            if background.isMotion_Y:
                self.animatedPanorama = True

        for foreground in self.foregrounds: #TODO - this will need to be it's own method, for easy ability to reload sprites
            if foreground.isAnimated:
                self.animatedPanorama = True
                foreground.image = loadAnimatedPanoramas(foreground)
            else:
                foreground.image = loadPanorama(foreground)
            if foreground.isMotion_X:
                self.animatedPanorama = True
            if foreground.isMotion_Y:
                self.animatedPanorama = True

        self.loadTileMapImages()

    def loadTileMapImages(self):
        if self.lowerTileMap.alpha:
            self.lowerTileMap.image = pygame.image.load(self.lowerTileMap.filePath).convert_alpha()
        else:
            self.lowerTileMap.image = pygame.image.load(self.lowerTileMap.filePath).convert()

        if self.upperTileMap.alpha:
            self.upperTileMap.image = pygame.image.load(self.upperTileMap.filePath).convert_alpha()
        else:
            self.upperTileMap.image = pygame.image.load(self.upperTileMap.filePath).convert()

    def debug_drawRenderQ(self):
        HOWTHICK = 1

        for renderBox in self.renderQueue:
            renderBox = [renderBox[0] - self.screenBoundryLeft(),
                         renderBox[1] - self.screenBoundryLeft(),
                         renderBox[2] - self.screenBoundryTop(),
                         renderBox[3] - self.screenBoundryTop()]

            pygame.draw.line(self.screen,
                             PRAM.COLOR_BLACK,
                             (renderBox[LEFT_EDGE], renderBox[TOP_EDGE]),
                             (renderBox[RIGHT_EDGE], renderBox[TOP_EDGE]),
                             HOWTHICK)
            pygame.draw.line(self.screen,
                             PRAM.COLOR_BLACK,
                             (renderBox[LEFT_EDGE], renderBox[TOP_EDGE]),
                             (renderBox[LEFT_EDGE], renderBox[BOTTOM_EDGE]),
                             HOWTHICK)
            pygame.draw.line(self.screen,
                             PRAM.COLOR_BLACK,
                             (renderBox[RIGHT_EDGE], renderBox[TOP_EDGE]),
                             (renderBox[RIGHT_EDGE], renderBox[BOTTOM_EDGE]),
                             HOWTHICK)
            pygame.draw.line(self.screen,
                             PRAM.COLOR_BLACK,
                             (renderBox[LEFT_EDGE], renderBox[BOTTOM_EDGE]),
                             (renderBox[RIGHT_EDGE], renderBox[BOTTOM_EDGE]),
                             HOWTHICK)
            pygame.draw.line(self.screen,
                             PRAM.COLOR_BLACK,
                             (renderBox[LEFT_EDGE], renderBox[TOP_EDGE]),
                             (renderBox[RIGHT_EDGE], renderBox[BOTTOM_EDGE]),
                             HOWTHICK)
            pygame.draw.line(self.screen,
                             PRAM.COLOR_BLACK,
                             (renderBox[RIGHT_EDGE], renderBox[TOP_EDGE]),
                             (renderBox[LEFT_EDGE], renderBox[BOTTOM_EDGE]),
                             HOWTHICK)

#use pygame image.load, convert alpha if necessary, return the image file
def loadPanorama(panorama):
    if panorama.alpha:
        return (pygame.image.load(panorama.filePath).convert_alpha(),) #tuple of one item
    else:
        return (pygame.image.load(panorama.filePath).convert(),)

#Images are named "0.<type>", "1.<type>", etc...
def loadAnimatedPanoramas(panorama):
    convertedImages = []
    for i in range(panorama.numbImages):
        if panorama.alpha:
            convertedImages.append(pygame.image.load(panorama.filePath+'\\' +str(i)+'.'+panorama.imageType).convert_alpha())
        else:
            convertedImages.append(pygame.image.load(panorama.filePath+'\\' +str(i)+'.'+panorama.imageType).convert())
    convertedImages = tuple(convertedImages)
    return convertedImages