from Game_Scene.Test.Mock_Classes.Grid_utility_mock import MockFlag

class ParticleMock:
    def __init__(self,
                 entity_id,
                 position,
                 world_size):
        self.entity_id = entity_id
        self._position = position
        #This would NOT be in a true particle class, but we are just faking physics system
        self.world_size = world_size
        self.checkBoundary()
        self.has_moved = MockFlag(True)

    def getEntityId(self):
        return self.entity_id

    def getPosition(self):
        return self._position

    def pan(self, pan): #[int, int, int]
        self._position[0] += pan[0]
        self._position[1] += pan[1]
        self._position[2] += pan[2]
        self.checkBoundary()
        self.has_moved.value = True

    #don't allow moving outside of the boundary of the world map
    def checkBoundary(self):
        if self._position[0] < 0:
            self._position[0] = 0
        if self._position[0] >= self.world_size[0]:
            self._position[0] = self.world_size[0] - 1
        if self._position[1] < 0:
            self._position[1] = 0
        if self._position[1] >= self.world_size[1]:
            self._position[1] = self.world_size[1] - 1
        #We will not use -Z offsets
        if self._position[2] < 0:
            self._position[2] = 0

    def move(self, position): #[int, int, int]
        #don't want to replace the list object, as this will kill the reference in sprite
        self._position[0] = position[0]
        self._position[1] = position[1]
        self._position[2] = position[2]
        self.checkBoundary()
        self.has_moved.value = True

    def update(self):
        pass

class ParticleComponentSystemMock:
    def __init__(self, world_size):
        #Since we don't have a real physics system, artificially create a boundary for the world map
        self.world_size = world_size
        self._active_particles = dict() #{(int)entity_id : Particle}
        self._inactive_particles = dict()

        self._entity_manager = None #Get the active entity_ids from here
        self._onscreen_entity_ids = None #shortcut to freqeuently accessed list

    def setEntityManager(self, entity_manager):
        self._entity_manager = entity_manager
        self._onscreen_entity_ids = self._entity_manager._onscreen_entity_ids

    def panParticle(self, entity_id, pan): #int, [int,int,int]
        try:
            if self._onscreen_entity_ids.get(entity_id) is not None:
                self._active_particles[entity_id].pan(pan)
        except:
            return False
        return True

    def moveParticle(self, entity_id, position): #int, [int,int,int]
        try:
            if self._onscreen_entity_ids.get(entity_id) is not None:
                self._active_particles[entity_id].move(position)
        except:
            return False
        return True

    def activateParticle(self, entity_id): #int
        try:
            self._active_particles[entity_id] = self._inactive_particles[entity_id]
            del(self._inactive_particles[entity_id])
        except:
            return False
        return True

    def deactivateParticle(self, entity_id): #int
        try:
            self._inactive_particles[entity_id] = self._active_particles[entity_id]
            del(self._active_particles[entity_id])
        except:
            return False
        return True

    def addParticle(self, entity_id, particle, active = True): #int, Particle, bool
        try:
            if active:
                self._active_particles[entity_id] = particle
            else:
                self._inactive_particles[entity_id] = particle
        except Exception as e:
                print("Exception caught during Particle.addParticle(): " + str(e))

    def removeParticle(self, entity_id):
        try:
            del(self._active_particles[entity_id])
        except:
            try:
                del (self._inactive_particles[entity_id])
            except:
                return False
        return True

    def update(self):
        try:
            for entity_id in self._onscreen_entity_ids.keys():
                try:
                    self._active_particles[entity_id].update
                except:
                    pass
        except Exception as e:
            print("Exception caught during ParticleComponentSystemMock.update(): " + str(e))
            return False
        return True

#notify onscreen/offscreen functions are ref by ptr in SceneManager corresponding scenes
class PhysicsSceneManager:
    def __init__(self):
        self._particle_component_systems = dict() #{scene_id : ParticleComponentSystemMock}
        self._active_component_systems = dict() #references to active elements in _particle_component_systems

    def addParticleComponentSystem(self, scene_id, particle_component_system):
        self._particle_component_systems[scene_id] = particle_component_system

    def removeParticleComponentSystem(self, scene_id):
        try:
            del (self._particle_component_systems[scene_id])
            del (self._active_component_systems[scene_id])
        except:
            pass

    def activateParticleComponentSystem(self, scene_id):
        try:
            self._active_component_systems[scene_id] = self._particle_component_systems[scene_id]
        except Exception as e:
            print("Exception caught during PhysicsSceneManager.activateParticleComponentSystem(): " + str(e))
            return False

    def deactivateParticleComponentSystem(self, scene_id):
        try:
            del(self._active_component_systems[scene_id])
        except:
            pass

    def addParticle(self, scene_id, entity_id, particle, active = True): #int, Particle, bool
        self._particle_component_systems[scene_id].addParticle(entity_id, particle, active)

    def removeParticle(self, entity_id, scene_id):
        ret_val =  self._particle_component_systems[scene_id].removeParticle(entity_id)
        return ret_val

    def panParticle(self, entity_id, pan, scene_id):
        try:
            #no action taken if the scene is not active
            return self._active_component_systems[scene_id].panParticle(entity_id, pan)
        except:
            pass

    def moveParticle(self, entity_id, position, scene_id): #int, [int,int,int]
        try:
            # no action taken if the scene is not active
            return self._active_component_systems[scene_id].moveParticle(entity_id, position)
        except:
            pass

    def update(self):
        try:
            for component_system in self._active_component_systems.values():
                component_system.update()
        except Exception as e:
            print("Exception caught during PhysicsSceneManager.update(): " + str(e))
            return False
        return True