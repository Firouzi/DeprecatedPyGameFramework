import pygame
from time import time
from scene_layer import SceneLayerFactory, SCENE_LAYER_TYPE
from resource_management_scene import RENDERABLE_LAYER_TYPE
import sys
sys.path.append("parameters\\")
import GRAPHICS_PARAM

class FPS_Calculator:
    def __init__(self):
        self.time_steps = list()
        self.index = 0
        self.MAX_STEPS = 10
        i = 0
        while i < self.MAX_STEPS:
            self.time_steps.append(0.0)
            i+=1

    def addTimeStep(self, time_s):
        self.time_steps[self.index] = time_s
        self.index += 1
        if self.index >= self.MAX_STEPS:
            self.index = 0

    #average framerate over the last MAX_STEPS samples
    def getFPS(self):
        count = 0
        fps_sum = 0
        for time_step in self.time_steps:
            fps_sum += time_step
            count +=1
        return 1 / (fps_sum/count) #FPS

class Renderer:
    def __init__(self,
                 window): #screen
        self.window = window

    def clearScreen(self):
        self.window.fill((0,0,0))

    def flipDisplay(self):
        pygame.display.flip()

    def renderImages(self,
                     renderables, #[Renderables]
                     camera_offset): #[int, int]
        x_min = camera_offset[0] #We will need to check the X position + the width of the image
        x_max = camera_offset[0] + GRAPHICS_PARAM.WINDOW_SIZE[0]
        y_min = camera_offset[1] #We will need to check the Y position + the width of the image
        y_max = camera_offset[1] + GRAPHICS_PARAM.WINDOW_SIZE[1]
        for renderable in renderables:
            if not renderable.isActive():
                continue
            #Start by checking if the renderable is on the screen
            world_coordinates = renderable.getWorldCoordinates()
            #see if they are not passed the right boundary, or the bottom boundary
            if world_coordinates[0] < x_max and world_coordinates[1] < y_max:
                image_coordinates = renderable.getImageCoordinates()
                #add the width of the image to it's origin to see if any is inside the left boundary
                if world_coordinates[0] + image_coordinates[2] > x_min:
                    #add the height of the image to it's origin to see if any is inside the top boundary
                    if world_coordinates[1] + image_coordinates[3] > y_min:
                        #render the image
                        image = renderable.getImage()
                        numb_rects = len(image_coordinates) // 4
                        screen_coordinates = renderable.getScreenCoordinates()  # [x1, y1, z1, x2, y2, z2,...]
                        assert (len(screen_coordinates) // 3 == numb_rects)
                        coordinate_index = 0
                        position_index = 0
                        count = 0
                        while count < numb_rects:
                            self.window.blit(image,
                                             (screen_coordinates[position_index],  # screen position x
                                              screen_coordinates[position_index + 1]),  # screen position y
                                             (image_coordinates[coordinate_index],  # tileMap x crop position
                                              image_coordinates[coordinate_index + 1],  # tileMap y crop position
                                              image_coordinates[coordinate_index + 2],  # tilemap  width
                                              image_coordinates[coordinate_index + 3]))  # tilemap height
                            coordinate_index += 4
                            position_index += 3
                            count += 1
            #This clause was removed due to adding floating tiles.  Because floating tiles are sorted on their
            #ground position, they will be past y_max but may still be visible on the screen
            #This code is very suboptimal, because every tile on the map must be checked for visibility
            #Futue improvements will return renderables only within quadrants that are on the screen
#            elif world_coordinates[1] >= y_max:
#                break #no more renderables on this layer will be on screen

    #When getting calculating coordinates, Panoramas handle the visibility issue, so that is not checked
    def renderPanorama(self,
                       renderables):
        for renderable in renderables:
            if not renderable.isActive():
                continue
            image = renderable.getImage()
            coordinates = renderable.getImageCoordinates() #[x1, y1, width1, height1, x2, y2, width2, height2,...]
            if len(coordinates) > 0: #might not be anything to render
                numb_rects = len(coordinates)//4
                position_px = renderable.getScreenCoordinates() #[x1, y1, z1, x2, y2, z2,...]
                assert(len(position_px)//3==numb_rects)
                coordinate_index = 0
                position_index = 0
                count = 0
                while count < numb_rects:
                    self.window.blit(image,
                                     (position_px[position_index],   # screen position x
                                      position_px[position_index+1]),  # screen position y
                                     (coordinates[coordinate_index],  # tileMap x crop position
                                      coordinates[coordinate_index+1],  # tileMap y crop position
                                      coordinates[coordinate_index+2],  # tilemap  width
                                      coordinates[coordinate_index+3]))  # tilemap height
                    coordinate_index+=4
                    position_index+=3
                    count+=1

    def combineSurface(self,
                       camera_offset,  # [int,int]
                       source_surface,  #pygame.surface
                       destination_surface,  #pygame.surface
                       coordinates): #pygame.surface
        return None #pygame.surface

class SceneHandler:
    def __init__(self,
                 window): # display window
        self._window = window

        self._renderer = Renderer(self._window)
        self._scene_layer_factory = SceneLayerFactory()
        self._fps_calculator = FPS_Calculator()
        self._camera_offset = (0,0) #Pushed to from Camera entity
        self._scene_layers = dict() #{layer_level_id : SceneLayer}

        self._previous_render_time = time()

    def receiveCameraOffset(self,
                            camera_offset): #[int, int]
        self._camera_offset = camera_offset

    def createSceneLayer(self,
                         layer_element_id,
                         layer_level_id,
                         resource_data):
        scene_layer = self._scene_layer_factory.createSceneLayer(layer_element_id = layer_element_id,
                                                                 layer_level_id = layer_level_id,
                                                                 resource_data = resource_data)
        self._scene_layers[layer_level_id] = scene_layer

    #Returns a Ptr object that can be sent back to scene layer with a Component
    def requestPtr(self,
                   layer_level_id):
        return self._scene_layers[layer_level_id].requestPtr()

    def addSceneComponent(self,
                          layer_level_id, #int
                          scene_component): #Renderable
        self._scene_layers[layer_level_id].addComponent(component = scene_component)

    def render(self,
               lag_normalized): #float [0.0,1.0)
        #handle frame rate
        current_render_time = time()
        elapsed_render_time = current_render_time - self._previous_render_time
        self._previous_render_time = current_render_time
        # if we are running too hot, spin the wheels for a bit
        if elapsed_render_time == 0 or (1 / elapsed_render_time) > GRAPHICS_PARAM.MAX_FRAMERATE:
            while time() - self._previous_render_time == 0 or (
                1 / (time() - self._previous_render_time)) > GRAPHICS_PARAM.MAX_FRAMERATE:
                pass
            current_render_time = time()
            elapsed_render_time = current_render_time - self._previous_render_time
            self._previous_render_time = current_render_time
        # if we we want to know the rendering framerate
        self._fps_calculator.addTimeStep(elapsed_render_time)

        self._renderer.clearScreen()
        #get all of the layers from the dictionary and sort them from bottom to top
        scene_layers = list(self._scene_layers.values())
        scene_layers.sort(key=lambda x: x.layer_level_id)
        for scene_layer in scene_layers:
            if scene_layer.scene_layer_type == SCENE_LAYER_TYPE.RENDERABLE:
                scene_layer.updateRenderableCoordinates(camera_offset = self._camera_offset,
                                                        lag_normalized = lag_normalized)
                renderables = scene_layer.getRenderables()
                if scene_layer.renderable_layer_type == RENDERABLE_LAYER_TYPE.PANORAMA:
                    self._renderer.renderPanorama(renderables = renderables)
                elif scene_layer.renderable_layer_type == RENDERABLE_LAYER_TYPE.IMAGE or \
                            scene_layer.renderable_layer_type == RENDERABLE_LAYER_TYPE.ATLAS or \
                            scene_layer.renderable_layer_type == RENDERABLE_LAYER_TYPE.MIXED:
                    self._renderer.renderImages(renderables = renderables,
                                                camera_offset = self._camera_offset)
        self._renderer.flipDisplay()
