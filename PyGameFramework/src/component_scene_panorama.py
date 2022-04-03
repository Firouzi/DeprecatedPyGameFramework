from component_system import SceneComponentSystem, SceneComponent, Renderable
import sys
sys.path.append("parameters\\")
import TIMING_PARAM, GRAPHICS_PARAM

#We need a renderable subcomponent to send to the scene layer
#But the Parent class holds all the needed data and logic
#So this proxy fulfills the subcomponent role but just passes all calls up to the Component
class PanoramaRenderableProxy(Renderable):
    def __init__(self, parent_component, component_element_id, layer_level_id, subcomponent_index):
        super(PanoramaRenderableProxy, self).__init__(parent_component, component_element_id, layer_level_id, subcomponent_index)
    def getImage(self):
        return self.parent_component.getImage()
    def calculateCoordinates(self, camera_offset, lag_normalized):
        return self.parent_component.calculateCoordinates(camera_offset, lag_normalized)
    def getImageCoordinates(self):
        return self.parent_component.getImageCoordinates()
    def isTilemap(self):
        return False
    def getTilePosition(self):
        return self.parent_component.getTilePosition()
    def getScreenCoordinates(self):
        return self.parent_component.getScreenCoordinates()

class PanoramaComponent(SceneComponent):
    def __init__(self,
                 scene_element_id,  #int
                 layer_element_id,  #int
                 layer_level_id, #int
                 images,  #[image]
                 image_size_px,  #(int, int,)
                 world_offset_px,  #(int, int,)
                 visible_sections,  #(int,)
                 movement_speed,  #(int, int,) - pixels per second
                 scroll_speed,  #(int, int, int, int,) - [Xmult, Xdiv, Ymult, Ydiv]
                 animation_lengths_ms): #(int,)
        SceneComponent.__init__(self,
                                scene_element_id = scene_element_id,
                                layer_element_id = layer_element_id,
                                layer_level_id = layer_level_id)
        #This fulfills the Renderable(Subcomponent) class, but will just return all render calls to here
        self._panorama_renderable_proxy = PanoramaRenderableProxy(parent_component = self,
                                                                  component_element_id=scene_element_id,
                                                                  layer_level_id = layer_level_id,
                                                                  subcomponent_index = 0)
        self._images = images
        self._image_size_px = image_size_px
        #_world_offset_px s where the top left corner of the image is placed in world coordinates
        #The default is to tile the image across the entire screen
        #Use visible sections to determine which parts int the game level actually show show
        self._world_offset_px = world_offset_px
        #visible_sections in sets of 4, which define boxes to display the panorama relative to world coordinates
        #each set of 4 is a box in the game space to display this image
        self._visible_sections = visible_sections
        #This scrolls the panorama image, it does not change it's position in the world
        self._movement_speed = movement_speed
        #determines how the panorama scrolls as the camera moves (Parallax scrolling)
        #This does not cause the panorama to move when the camera is still
        self._scroll_speed = scroll_speed
        #how long it takes to go through the sequence of images
        self._animation_lengths_ms = animation_lengths_ms

        self._numb_images = len(images)
        self._numb_visible_sections = len(self._visible_sections) // 4
        self._frame_timer = 0
        self._current_frame_index = 0
        self._scrolling_offset = [0,0]
        self._moving_offset = [0.0, 0.0] #add as float every update but will be rounded for rendering
        self._image_coordinates = list()
        self._screen_coordinates = list()
        #We only need to update the position when we are going to render the image
        #until then, just keep a count of how many increments we need to move
        self._numb_updates = 0 #this grows forever
        self._animation_updates = 0 #we reset this every time we flip the animation frame

        #speed up/slow down animation, scrolling and movement
        self._animation_scaling_factor = 1.0
        self._move_scaling_factor = (1,1)
        self._scroll_scaling_factor = (1,1)
        self._IS_ANIMATED = self._numb_images > 1

    #We just update the animation timer here, we won't calculate the actual image
    #until time for render, because we will not render on every update
    def update(self):
        self._animation_updates +=1
        self._numb_updates +=1

    def getImage(self):
        return self._images[self._current_frame_index]

    #This will be called when the renderer is ready to display the image
    #We have to factor in 2 types of potential movement, parallex scrolling and image movement
    #Image movement occurs based on timer, parallax scrolling occurs based on camera position
    def calculateCoordinates(self,
                             camera_offset, #[int, int]
                             lag_normalized): #float [0.0,1.0)
        if self._IS_ANIMATED:
            self._frame_timer += int((TIMING_PARAM.MS_PER_UPDATE * self._animation_updates) * self._animation_scaling_factor)
            self._animation_updates = 0
            if self._frame_timer >= self._animation_lengths_ms[self._current_frame_index]:
                self._frame_timer = 0
                self._current_frame_index+=1
                if self._current_frame_index >= self._numb_images:
                    self._current_frame_index = 0

        self._image_coordinates = list()
        self._screen_coordinates = list()
        #parallax scrolling
        scroll_offset = [camera_offset[0]*self._scroll_speed[0]//self._scroll_speed[1],
                         camera_offset[1]*self._scroll_speed[2]//self._scroll_speed[3]]
        image_offset = [0,0]
        #if the image moves horizontally, apply the offset.
        lag_offsetX = 0
        if abs(self._movement_speed[0])> 0:
            # (# Pixels/Second)*(1 Second/1000ms)* (# milleseconds elapsed)
            self._moving_offset[0] += self._movement_speed[0]/1000 * \
                                      self._move_scaling_factor[0]* \
                                      self._numb_updates*TIMING_PARAM.MS_PER_UPDATE
            lag_offsetX = (lag_normalized * TIMING_PARAM.MS_PER_UPDATE) * (self._movement_speed[0] / 1000)
        #do the same for vertical movement
        lag_offsetY = 0
        if abs(self._movement_speed[1])> 0:
            self._moving_offset[1] += self._movement_speed[1]/1000 * \
                                      self._move_scaling_factor[1]* \
                                      self._numb_updates*TIMING_PARAM.MS_PER_UPDATE
            lag_offsetY = (lag_normalized * TIMING_PARAM.MS_PER_UPDATE) * (self._movement_speed[1]/1000)
        image_offset[0] = round(self._moving_offset[0] + scroll_offset[0] + lag_offsetX) + self._world_offset_px[0]
        image_offset[1] = round(self._moving_offset[1] + scroll_offset[1] + lag_offsetY) + self._world_offset_px[1]

        #We don't want to keep growing value of self._moving_offset, so 'reset' it with modulos operation
        if abs(self._moving_offset[0]) > 0:
            if self._moving_offset[0] > 0:
                self._moving_offset[0] = self._moving_offset[0] % self._image_size_px[0]
            else:
                self._moving_offset[0] = -(abs(self._moving_offset[0])%self._image_size_px[0])
        if abs(self._moving_offset[1]) > 0:
            if self._moving_offset[1] > 0:
                self._moving_offset[1] = self._moving_offset[1] % self._image_size_px[1]
            else:
                self._moving_offset[1] = -(abs(self._moving_offset[1]) % self._image_size_px[1])

        #Do a modulus to wrap the image if it has scrolled farther than it's length
        if image_offset[0] >=0:
            image_offset[0] %=self._image_size_px[0]
        else:
            image_offset[0] = -(abs(image_offset[0])%self._image_size_px[0])
        if image_offset[1] >=0:
            image_offset[1] %=self._image_size_px[1]
        else:
            image_offset[1] = -(abs(image_offset[1])%self._image_size_px[1])

        #each visual section is 4 ints [xStart, yStart, width, length]
        vs_index = 0 #incremencted by 4 at a time
        count = 0
        numb_vs = len(self._visible_sections)//4
        while count < numb_vs:
            if self._isOnScreen(visible_section = self._visible_sections[vs_index : vs_index+4],
                                camera_offset = camera_offset):
                #we need to tile the image horizontally and vertically
                #we will make squares from left to right, then go down to the next
                #row and repeate, until the entire visibile section has been covered

                ### FIND BOUNDARIES OF IMAGE ###

                #How far the panorama is offset from left edge of the screen
                xOffset = 0
                if self._visible_sections[vs_index] > camera_offset[0]:
                    xOffset = self._visible_sections[vs_index] - camera_offset[0]
                #How far the panorama is offset from top edge of the screen
                yOffset = 0
                if self._visible_sections[vs_index+1] > camera_offset[1]:
                    yOffset = self._visible_sections[vs_index+1] - camera_offset[1]

                #size of image square to draw
                xRange = (self._visible_sections[vs_index] + self._visible_sections[vs_index+2]) - (camera_offset[0] + xOffset)
                #if the size of the image goes off the right edge of the screen, trim to the width of the screen
                if xRange + xOffset > GRAPHICS_PARAM.WINDOW_SIZE[0]:
                    xRange = GRAPHICS_PARAM.WINDOW_SIZE[0] - xOffset
                yRange = (self._visible_sections[vs_index+1] + self._visible_sections[vs_index+3]) - (camera_offset[1] + yOffset)
                # if the size of the image goes off the bottom edge of the screen, trim to the height of the screen
                if yRange + yOffset > GRAPHICS_PARAM.WINDOW_SIZE[1]:
                    yRange = GRAPHICS_PARAM.WINDOW_SIZE[1] - yOffset

                currentXrange = xRange  # size of block of image to blit
                currentYrange = yRange
                covered_yRange = 0 #The total amount of screen in thy Y direction covered
                currentScreenPos = [xOffset, yOffset] #absolute screen position to blit to

                #coordinates of image to start from
                currentCropX = (image_offset[0] + xOffset) % self._image_size_px[0]
                currentCropY = (image_offset[1] + yOffset) % self._image_size_px[1]
                keepGoing = True
                shiftX = False
                shiftY = False

                #This is true until we have covered the entire range of the visible section (fitting on the screen)
                while keepGoing:
                    if currentCropX + currentXrange > self._image_size_px[0]:
                        currentXrange = self._image_size_px[0] - currentCropX
                        shiftX = True
                    if currentCropY + currentYrange > self._image_size_px[1]:
                        currentYrange = self._image_size_px[1] - currentCropY
                        shiftY = True

                    #add the box to the list
                    self._screen_coordinates.append(currentScreenPos[0]) #draw X position
                    self._screen_coordinates.append(currentScreenPos[1]) #draw Y position
                    self._screen_coordinates.append(0) #No Z offset for panoramas
                    self._image_coordinates.append(currentCropX)
                    self._image_coordinates.append(currentCropY)
                    self._image_coordinates.append(currentXrange)
                    self._image_coordinates.append(currentYrange)

                    # blit across the X direction first, then shift down the Y and reset the X
                    if shiftX:
                        currentScreenPos = [currentScreenPos[0] + currentXrange, currentScreenPos[1]]
                        currentCropX = (currentCropX + currentXrange) % self._image_size_px[0]
                        currentXrange = xRange - currentXrange
                        #Don't go beyond the edge of the visible section
                        if currentXrange + currentScreenPos[0] + camera_offset[0] > \
                                        self._visible_sections[vs_index] + self._visible_sections[vs_index+2]:
                            currentXrange = (self._visible_sections[vs_index] + self._visible_sections[vs_index+2]) - \
                                            (currentScreenPos[0] + camera_offset[0])
                        shiftX = False
                    elif shiftY:
                        covered_yRange += currentYrange
                        #If we have covered the entire screen vertically, we do not shift down again
                        if covered_yRange >= yRange:
                            keepGoing = False
                        else:
                            currentScreenPos = [xOffset, currentScreenPos[1] + currentYrange]
                            currentCropX = (image_offset[0] + xOffset) % self._image_size_px[0]
                            currentXrange = xRange
                            currentCropY = (currentCropY + currentYrange) % self._image_size_px[1]
                            currentYrange = yRange - currentYrange
                            # Don't go beyond the edge of the visible section
                            if currentYrange + currentScreenPos[1] + camera_offset[1] > \
                                            self._visible_sections[vs_index+1] + self._visible_sections[vs_index+3]:
                                currentYrange = (self._visible_sections[vs_index+1] + self._visible_sections[vs_index+3]) - \
                                                (currentScreenPos[1] + camera_offset[1])
                            shiftY = False
                    else:
                        keepGoing = False  # you have blitted the entire visible section
            vs_index +=4
            count +=1
        self._numb_updates = 0 #reset the count for the next set of updates

    def getImageCoordinates(self):
        return self._image_coordinates

    def getScreenCoordinates(self):
        return self._screen_coordinates

    def isTilemap(self):
        return False  # Boolean

    def getRenderables(self):
        return [self._panorama_renderable_proxy]

    def kill(self):
        self._panorama_renderable_proxy.deactivate()
        self.deactivate()

    def _isOnScreen(self,
                    visible_section, #[x: int, y : int, width : int, heigt : int]
                    camera_offset): #[x :int, y :int]
        if (visible_section[0] + visible_section[2] > camera_offset[0] and  #right edge
            visible_section[0] < camera_offset[0] + GRAPHICS_PARAM.WINDOW_SIZE[0] and # left edge
            visible_section[1] + visible_section[3] > camera_offset[1] and #bottom edge
            visible_section[1] < camera_offset[1] + GRAPHICS_PARAM.WINDOW_SIZE[1]): #top edge
            return True
        return False

class PanoramaComponentSystem(SceneComponentSystem):
    def __init__(self):
        super(PanoramaComponentSystem, self).__init__()
        self._panorama_components = dict()  # {int : component}

    def update(self):
        for panorama_component in self._panorama_components.values():
            panorama_component.update()

    def getSceneComponents(self,
                           component_element_id):
        try:
            return self._panorama_components[component_element_id].getRenderables()
        except:
            return list() #empty set if there is no element with this id

    def createComponent(self,
                        scene_element_id, #int
                        layer_element_id, #int
                        layer_level_id, #int
                        resource_data): #PanoramaResourceData
        panorama_component = PanoramaComponent(scene_element_id = scene_element_id,
                                               layer_element_id = layer_element_id,
                                               layer_level_id = layer_level_id,
                                               images = resource_data.images,
                                               image_size_px = resource_data.image_size_px,
                                               world_offset_px = resource_data.world_offset_px,
                                               visible_sections = resource_data.visible_sections,
                                               movement_speed = resource_data.movement_speed,
                                               scroll_speed = resource_data.scroll_speed,
                                               animation_lengths_ms = resource_data.animation_lengths_ms)
        self._panorama_components[scene_element_id] = panorama_component
        return panorama_component
