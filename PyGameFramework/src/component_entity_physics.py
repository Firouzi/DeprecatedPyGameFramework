from component_system import EntityComponentSystem, EntityComponent, Subcomponent

#container class for the PhysicsResourceData to use to define particle data
class ParticleData:
    def __init__(self,
                 inverse_mass, #float
                 damping, #float
                 offsets,): #(int,) - if a child particle
        self.inverse_mass = inverse_mass
        self.damping = damping
        self.offsets = offsets

class Particle(Subcomponent):
    def __init__(self,
                 parent_component,
                 component_element_id,  #int
                 layer_level_id, #int
                 subcomponent_index,  #int
                 position,  #[int, int, int]
                 inverse_mass,  #float
                 velocity,  #[int, int, int]
                 acceleration,  #[int, int, int]
                 damping,  #float
                 orientation): #[float, float]
        super(Particle, self).__init__(parent_component = parent_component,
                                       component_element_id=component_element_id,
                                       layer_level_id = layer_level_id,
                                       subcomponent_index = subcomponent_index)
        self._position = position
        self._inverse_mass = inverse_mass
        self._velocity = velocity
        self._acceleration = acceleration
        self._damping = damping
        self._orientation = orientation

        self._force_accumulator = [0.0, 0.0, 0.0]

    def setPosition(self,
                    position): #[int, int, int]
        self._position = position

    def setVelocity(self,
                    velocity): #[int, int, int]
        self._velocity = velocity

    def setAcceleration(self,
                        acceleration): #[int, int, int]
        self._acceleration = acceleration

    def setOrientation(self,
                       orientation): #[int, int, int]
        self._orientation = orientation

    def getPosition(self):
        return self._position

    def getVelocity(self):
        return self._velocity

    def getOrientation(self):
        return self._orientation

    def addForce(self,
                 force): #[float, float, float]
        self._force_accumulator[0] += force[0]
        self._force_accumulator[1] += force[1]
        self._force_accumulator[2] += force[2]

    def integrate(self,
                  duration): #float
        self._position[0] += int(self._force_accumulator[0])
        self._position[1] += int(self._force_accumulator[1])
        self._position[2] += int(self._force_accumulator[2])
        self._force_accumulator = [0.0, 0.0, 0.0]

#A simple particle which has its position determined only by it's parent particle
class ParticleChild(Particle):
    def __init__(self,
                 parent_component,
                 component_element_id,  #int
                 layer_level_id, #int
                 subcomponent_index,  #int
                 position,  #int[9] OR int[17], the last index is always height
                 inverse_mass,  #float
                 velocity,  #[int, int, int]
                 acceleration,  #[int, int, int]
                 damping,  #float
                 orientation,  #[float, float]
                 parent_particle): #*Particle
        super(ParticleChild, self).__init__(parent_component = parent_component,
                                            component_element_id = component_element_id,
                                            layer_level_id = layer_level_id,
                                            subcomponent_index = subcomponent_index,
                                            position = position,
                                            inverse_mass = inverse_mass,
                                            velocity = velocity,
                                            acceleration = acceleration,
                                            damping = damping,
                                            orientation = orientation)
        self.parent_particle = parent_particle

    def integrate(self,
                  duration): #float
        return #Child Particles can't be moved independantly from Parents

#We will need to know which direction the parent is facing, then we will get the offset from that direction
#Position might be for a 4 way or an 8 way array, we will know by it's length
#The height offset will always be the last index since it's the same in any orientation
    def getPosition(self):
        #TODO - use the orientaion to determine the direction and the relative position
        direction_multiplier = 1
        if len(self._position) == 17: #8 way
            direction_multiplier = 1
        else: #4 way
            direction_multiplier = 1
        direction_multiplier*=2 #2 coordinates
        return [self._position[direction_multiplier] + self.parent_particle.getPosition()[0],  #X child offset + parent
                self._position[direction_multiplier + 1] + self.parent_particle.getPosition()[1],  #Y child offset + parent
                self._position[-1] + self.parent_particle.getPosition()[2]]#Z child offset + parent

class ParticleContact:
    def __init__(self,
                 particle, #*Particle
                 restitution, #float
                 contact_normal, #[int, int]
                 penetration):
        self.particle = particle
        self.restitution = restitution
        self.contact_normal = contact_normal
        self.penetration = penetration

    def resolve(self,
                duration): #float
        pass

    def resolveInterpenetration(self,
                                duration): #float
        pass

    def resolveVelocity(self,
                        duration): #float
        pass

class ParticleParticleContact(ParticleContact):
    def __init__(self,
                 particle,  #*Particle
                 restitution,  #float
                 contact_normal,  #[int, int]
                 penetration,  #float
                 particle2): #*Particle
        super(ParticleParticleContact, self).__init__(particle, restitution, contact_normal, penetration)
        self.particle2 = particle2

class ParticleEnvironmentContact(ParticleContact):
    def __init__(self,
                 particle, #*Particle
                 restitution, #float
                 contact_normal, #[int, int]
                 penetration, #float
                 environment_component): #*EnvironmentComponent
        super(ParticleEnvironmentContact, self).__init__(particle, restitution, contact_normal, penetration)
        self.environment_component = environment_component

    def resolveDamping(self,
                       duration): #float
        pass

    def resolveAcceleration(self,
                            duration): #float
        pass

    def resolvePosition(self,
                        duration): #float
        pass

class ParticleBarrierContact(ParticleContact):
    def __init__(self,
                 particle,  # *Particle
                 restitution,  #float
                 contact_normal,  #[int, int]
                 penetration,  #float
                 barrier_component): #*BarrierComponent
        super(ParticleBarrierContact, self).__init__(particle, restitution, contact_normal, penetration)
        self.bar_component = barrier_component

class ParticleEventContact(ParticleContact):
    def __init__(self,
                 particle,  # *Particle
                 restitution,  #float
                 contact_normal,  #[int, int]
                 penetration,  #float
                 event_component): #*EventComponent
        super(ParticleEventContact, self).__init__(particle, restitution, contact_normal, penetration)
        self.particle = particle
        self.event_component = event_component

class ParticleContactEntry: #used to register particles to contact generators
    def __init__(self):
        pass

    def getID(self):
        return [0] #[int]

class ParticleLinkEntry(ParticleContactEntry):
    def __init__(self,
                 particle_ids, #[int,int]
                 length): #int
        super(ParticleLinkEntry, self).__init__()
        self.particle_ids = particle_ids
        self.length = length

    def getID(self):
        return self.particle_ids

class ParticleContactGenetator:
    def __init(self):
        self.is_active = False
        self.particle_contact_entries = dict() #{[int] : ParticleContactEntry}

    def generateContacts(self):
        return list() #[ParticleContact]

    def registerParticleContact(self,
                                  particle_contact_entry): #[int]
        self.particle_contact_entries[particle_contact_entry.getID()] = particle_contact_entry

    def unregisterParticleContact(self,
                                    particle_contact_entry):
        try:
            del self.particle_contact_entries[particle_contact_entry.getID()]
            return True
        except:
            return False

class ParticleLinkGenerator(ParticleContactGenetator):
    def __init__(self):
        super(ParticleLinkGenerator, self).__init__()

    def generateContacts(self):
        return list() #[ParticleContact]

class ParticleCableGenerator(ParticleLinkGenerator):
    def __init__(self):
        super(ParticleCableGenerator, self).__init__()

    def generateContacts(self):
        return list() #[ParticleContact]

class ParticleRodGenerator(ParticleLinkGenerator):
    def __init__(self):
        super(ParticleRodGenerator, self).__init__()

    def generateContacts(self):
        return list() #[ParticleContact]

class CollisionDetector:
    def __init__(self):
        pass

    def detectCollisions(self):
        return list() #[ParticleContact]

class ContactResolver:
    def __init__(self):
        pass

    def resolveContact(self,
                       particle_contact): #*ParticleContact
        pass

class ParticleForceGenerator:
    def __init__(self):
        self.particles = dict() #{(entity_id, particle_id) : *Particle}

    def registerParticle(self,
                         particle): #Particle
        self.particles[(particle.getElementId(), particle.getSubcomponentIndex)] = particle

    def removeParticle(self,
                       particle): #Particle
        try:
            del self.particles[(particle.getElementId(), particle.getSubcomponentIndex)]
            return True
        except:
            return False

    def updateForce(self,
                    duration): #float
        pass

class EntityPhysicsComponent(EntityComponent):
    def __init__(self,
                 entity_element_id,  #int
                 layer_level_id, #int
                 particles): #(Particle,)
        super(EntityPhysicsComponent, self).__init__(entity_element_id = entity_element_id,
                                                     layer_level_id = layer_level_id)
        self._particles = particles

    def initialize(self):
        self._particles = tuple(self._particles)

    def kill(self): #No Ptr's sent out, no need to free anything
        pass

    #we always set the position (etc) of the parent particle
    def setPosition(self,
                    position): #[int, int, int]
        self._particles[0].setPosition(position = position)

    def setVelocity(self,
                    velocity): #[int, int, int]
        self._particles[0].setVelocity(velocity = velocity)

    def setAcceleration(self,
                        acceleration): #[int, int, int]
        self._particles[0].setAcceleration(acceleration = acceleration)

    def setOrientation(self,
                       orientation): #[int, int, int]
        self._particles[0].setOrientation(orientation = orientation)

    def getOrientation(self,
                       particle_index): #int
        return self._particles[particle_index].orientation

    def getPosition(self,
                       particle_index): #int
        return self._particles[particle_index].getPosition()

    def getVelocity(self,
                       particle_index): #int
        return self._particles[particle_index].velocity

    def integrate(self,
                  duration): #float
        for particle in self._particles:
            particle.integrate(duration)

    def addForce(self,
                 particle_index, #int
                 force): #[float, float, float]
        self._particles[particle_index].addForce(force)

    def getParticle(self,
                    particle_index):
        return self._particles[particle_index]

    #not actually using the Ptr class since the particle classes are persistent
    def getParticlePtrs(self):
        return self._particles

    def update(self): #float
        for particle in self._particles:
            particle.integrate(5.0)

class PhysicsComponentSystem(EntityComponentSystem):
    def __init__(self):
        super(PhysicsComponentSystem, self).__init__()
        self.collision_detector = CollisionDetector()
        self.contact_resolver = ContactResolver()
        self.force_generators = dict() #{force_generator_id : ForceGenerator}
        self.particle_contact_generators = dict() #{contact_generator_id : ParticleContactGenetator}
        self._entity_physics_components = dict()#{int : component}
        self.send_contact = None #func pointer tp behavior system receive contact method

    def removeComponent(self,
                        component_element_id): #int
        try:
            self._entity_physics_components[component_element_id].kill() #TODO - does nothing, not needed?
            del self._entity_physics_components[component_element_id]
            return True
        except:
            return False

    def setPosition(self,
                    entity_id, #int
                    position): #[int, int, int]
        try:
            self._entity_physics_components[entity_id].setPosition(position = position)
        except:
            assert (1 == 2)

    def setVelocity(self,
                    entity_id, #int
                    velocity): #[int, int, int]
        try:
            self._entity_physics_components[entity_id].setVelocity(velocity = velocity)
        except:
            assert (1 == 2)

    def setAcceleration(self,
                        entity_id, #int
                        acceleration): #[int, int, int]
        try:
            self._entity_physics_components[entity_id].setAcceleration(acceleration = acceleration)
        except:
            assert (1 == 2)

    def setOrientation(self,
                       entity_id, #int
                       orientation): #[int, int, int]
        try:
            self._entity_physics_components[entity_id].setOrientation(orientation = orientation)
        except:
            assert (1 == 2)

    def getOrientation(self,
                       entity_id, #int
                       particle_index): #int
        try:
            return self._entity_physics_components[entity_id].getOrientation(particle_index = particle_index)
        except:
            assert (1 == 2)

    def getPosition(self,
                    entity_id, #int
                    particle_index): #int
        try:
            return self._entity_physics_components[entity_id].getPosition(particle_index = particle_index)
        except:
            assert (1 == 2)

    def getVelocity(self,
                       entity_id, #int
                       particle_index): #int
        try:
            return self._entity_physics_components[entity_id].getVelocity(particle_index = particle_index)
        except:
            assert(1==2)

    def createComponent(self,
                        component_element_id,  #int
                        layer_level_id, #int
                        resource_data): #PhysicsResourceData
        is_parent = True #true on first loop
        parent_particle = None #first created particle passed to all children
        particles = list()
        #create component first because subcomponents need the reference
        entity_physics_component = EntityPhysicsComponent(entity_element_id= component_element_id,
                                                          layer_level_id =layer_level_id,
                                                          particles = particles)

        for particle_data in resource_data.particle_datas:
            #First particle in an entity is always the parent, then we make child particles
            if is_parent:
                parent_particle = Particle(parent_component = entity_physics_component,
                                           component_element_id=component_element_id,
                                           layer_level_id = layer_level_id,
                                           subcomponent_index= 0,
                                           position = [0,0,0],
                                           inverse_mass = particle_data.inverse_mass,
                                           velocity = [0,0,0],
                                           acceleration = [0,0,0],
                                           damping = particle_data.damping,
                                           orientation = [0.0, 0.0])
                particles.append(parent_particle)
                is_parent = False
            else:
                particles.append(ParticleChild(parent_component = entity_physics_component,
                                               component_element_id = component_element_id,
                                               layer_level_id = layer_level_id,
                                               subcomponent_index= 0,
                                               position = particle_data.offsets,
                                               inverse_mass = particle_data.inverse_mass,
                                               velocity = [0,0,0],
                                               acceleration = [0,0,0],
                                               damping = particle_data.damping,
                                               orientation = [0.0, 0.0],
               #this is not the same as parent_component which is a Component, parent_particle is a Subcomponent
                                               parent_particle = parent_particle))
        entity_physics_component.initialize()
        self._entity_physics_components[component_element_id] = entity_physics_component

    def receiveForce(self,
                     entity_id, #int
                     particle_index, #int
                     force): #[float, float, float]
        try:
            self._entity_physics_components[entity_id].addForce(particle_index, force)
            return True
        except:
            return False

    def registerToForceGenerator(self,
                                 entity_id, #int
                                 particle_index, #int
                                 forge_generator_id): #int
        try:
            self.force_generators[forge_generator_id].registerParticle(
                self._entity_physics_components[entity_id].getParticle(particle_index))
            return True
        except:
            return False

    def unregisterFromForceGenerator(self,
                                 entity_id, #int
                                 particle_index, #int
                                 forge_generator_id): #int
        if self._entity_physics_components.get(entity_id) is not None:
            self.force_generators[forge_generator_id].removeParticle(
                self._entity_physics_components[entity_id].getParticle(particle_index))

    def registerToContactGenerator(self,
                                   particle_contact_entry, #ParticleContactEntry
                                   contact_generator_id): #int
        self.particle_contact_generators[contact_generator_id].registerParticleContact(particle_contact_entry)

    def unregisterFromContactGenerator(self,
                                   particle_contact_entry, #ParticleContactEntry
                                   contact_generator_id): #int
        self.particle_contact_generators[contact_generator_id].unregisterParticleContact(particle_contact_entry)

    def getParticlePtrs(self,
                        component_element_id):
        try:
            return self._entity_physics_components[component_element_id].getParticlePtrs()
        except:
            return tuple()

    def update(self):
        for entity_physics_component in self._entity_physics_components.values():
            entity_physics_component.update()

