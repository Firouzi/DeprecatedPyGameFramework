#Sprite Visible does not require physics or behavior to be activated, if static images are desired
    #Sprite with only behavior is a stationary animated object that does not interact with other entities
    #Sprite with only phyics true can move around but not animate
    #Sprite without AI cannot make independant actions, though can be interacted with physically

#Entity Always Active sets everything to true, and activates everything

#Although it is allowed to have different combinations of these components true/false, specific entities may
    #not function correctly in a given state.

#Linked Entities always have the same status applied to them

#EntityStatus indexes
#An inactive sprite has no effect on any component, cannot interact with other nodes, cannot change behavior or move
ACTIVATED_INDEX = 0 #Bool
#If AA is True, Node is always updated, and allowed to move even if not in an active cell.
ALWAYS_ACTIVE_INDEX = 1 #Bool
#If not visible, sprite will not be rendered, but still has an active bounding box
SPRITE_VISIBLE_INDEX = 2 #Bool
#If ETHEREAL is True, This means no collision detection
ETHEREAL_INDEX = 3 #Bool
#If physics is not active, the node is frozen (though still can be collided with)
PHYSICS_ACTIVE_INDEX = 4 #Bool
#If behavior is inactive, cannot update frame or state or react to input
BEHAVIOR_ACTIVE_INDEX = 5 #Bool
#If AI is inactive, than the node will not make any new decisions
AI_ACTIVE_INDEX = 6 #Bool
#Dependent nodes must have the same state, meaning if one is in an active cell all are active
#This is to prevent a situation where the lower portion of a character is a sprite in an active cell,
#wheras the upper portion is a sprite in an inactive cell, and the legs walk away from the torso!
DEPENDENT_ENTITIES_INDEX = 7 #[Int], Make the same change to all entitis in this list


#The entity system tracks all of the current active entity id's, and assigns new entity ids
#The entity system notifies component systems when entities are active or inactive
#One of the most important functions of the EM is to receive input from the scene_handler that a sprite is
#not on screen - EM will notify the other components to deactivate that entity to remove overhead of updating them
#entities can also be permantly active (even offscreen), made invisible, or temporarily deactivated
class EntitySystem:
    def __init__(self,
                 particle_component_system,
                 behavior_component_system,
                 ai_component_system,
                 scene_handler):
        self._particle_component_system = particle_component_system
        self._behavior_component_system = behavior_component_system
        #This is the active scene, and will be updated by the game engine when it changes
        self._scene_handler = scene_handler
        self._ai_component_system = ai_component_system

        #the list uses the "<component>_ACTIVE_INDEX" values
        self._entity_status_lists = dict() #{entity_id : list()}
        #This is a list of keys to send to updating components for any entities on screen
        #don't re initialize this as components are using the same reference
        self._onscreen_entity_ids = dict() #{entity_id: True}

    #This status would be set by game_engine, not by one of the entity components
    #This does not change the status of individual components, only the overall status
    #Activates entity for any components with active status and pending message
    #Checks to see if sprite is onscreen (or always active), activating other components if True
    def activateEntity(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            if not entity_status[ACTIVATED_INDEX]:
                entity_status[ACTIVATED_INDEX] = True
                self._scene_handler.activateEntity(entity_id)
                #There is not need for a FalsePending check for Physics/Behavior/AI
                #When entity status was deactivated, those were set as inactive
                if self._scene_handler.spriteIsInActiveCell(entity_id) or entity_status[ALWAYS_ACTIVE_INDEX]:
                    self._onscreen_entity_ids[entity_id] = True
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._activateEntityDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("activateEntity(): ",entity_id)
            return False
        return True

    def _activateEntityDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            if not dependant_entity_status[ACTIVATED_INDEX]:
                dependant_entity_status[ACTIVATED_INDEX] = True
                self._scene_handler.activateEntity(dependant_entity_id)
                #There is not need for a FalsePending check for Physics/Behavior/AI
                #When entity status was deactivated, those were set as inactive
                if self._scene_handler.spriteIsInActiveCell(dependant_entity_id) or dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                    self._onscreen_entity_ids[dependant_entity_id] = True
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_activateEntityDependant(): ",dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #This does not change the status of individual components, and deactives them all
    #If reactivated, each component returns to previous state
    def deactivateEntity(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            if entity_status[ACTIVATED_INDEX]:
                try:
                    del(self._onscreen_entity_ids[entity_id])
                except:
                    pass
                entity_status[ACTIVATED_INDEX] = False
                self._scene_handler.deactivateEntity(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._deactivateEntityDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("deactivateEntity(): ",entity_id)
            return False
        return True

    def _deactivateEntityDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            if dependant_entity_status[ACTIVATED_INDEX]:
                try:
                    del(self._onscreen_entity_ids[dependant_entity_id])
                except:
                    pass
                dependant_entity_status[ACTIVATED_INDEX] = False
                self._scene_handler.deactivateEntity(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_deactivateEntityDependant(): ",dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #Likely added right after building the individual entities
    #choose 1 entity to be the 'master', and add all dependant entities to it
    #cannot add a dependant with a dependant to an entity
    #TODO - we may not need to have the same status for visible/ethereal
    def addEntityDependancy(self, entity_id, dependant_entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            #If this entity is already in the dependants list
            if dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                print("Adding " + str(dependant_entity_id) + " as dependant to " + str(entity_id))
                print("This relationship already exists.")
                return True
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            if len(dependant_entity_status[DEPENDENT_ENTITIES_INDEX]) > 0:
                print("Cannot add dep_id " + str(dependant_entity_id) + " to ent_id " + str(entity_id))
                print("The dependant already has dependants")
                assert(1==2)

            if entity_status[ALWAYS_ACTIVE_INDEX]:
                if not dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                    self._setDependantAlwaysActive(dependant_entity_id)
            elif dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                    self._removeEntityAlwaysActiveDependant(dependant_entity_id)
            if entity_status[ACTIVATED_INDEX]:
                if not dependant_entity_status[ACTIVATED_INDEX]:
                    self._activateEntityDependant(dependant_entity_id)
            elif dependant_entity_status[ACTIVATED_INDEX]:
                    self._deactivateEntityDependant(dependant_entity_id)
            if entity_status[SPRITE_VISIBLE_INDEX]:
                self._setEntitySpriteDependantVisible(dependant_entity_id)
            else:
                self._setSpriteDependantInvisible(dependant_entity_id)
            if entity_status[ETHEREAL_INDEX]:
                self._setSpriteDependantEthereal(dependant_entity_id)
            else:
                self._setSpriteDependantTangible(dependant_entity_id)
            if entity_status[PHYSICS_ACTIVE_INDEX]:
                self._activateEntityPhysicsDependant(dependant_entity_id)
            else:
                self._deactivateEntityPhysicsDependant(dependant_entity_id)
            if entity_status[BEHAVIOR_ACTIVE_INDEX]:
                self._activateEntityBehaviorDependant(dependant_entity_id)
            else:
                self._deactivateEntityBehaviorDependant(dependant_entity_id)
            if entity_status[AI_ACTIVE_INDEX]:
                self._activateEntityAiDependant(dependant_entity_id)
            else:
                self._deactivateEntityAIDependant(dependant_entity_id)

            #Add all current_dependant_id's to the new dependant_entity
            #Add the new dependant_entity to all current_dependant_id's
            for current_dependant_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                dependant_entity_status[DEPENDENT_ENTITIES_INDEX].append(current_dependant_id)
                self._scene_handler.addEntityDependancy(dependant_entity_id, current_dependant_id)
                self._entity_status_lists[current_dependant_id][DEPENDENT_ENTITIES_INDEX].append(dependant_entity_id)
                self._scene_handler.addEntityDependancy(current_dependant_id, dependant_entity_id)
            #add the master entity to new dependant_entity
            dependant_entity_status[DEPENDENT_ENTITIES_INDEX].append(entity_id)
            self._scene_handler.addEntityDependancy(dependant_entity_id, entity_id)
            #finally add the new dependant_entity to the master entity
            entity_status[DEPENDENT_ENTITIES_INDEX].append(dependant_entity_id)
            self._scene_handler.addEntityDependancy(entity_id, dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("addEntityDependancy(): ",entity_id, dependant_entity_id)
            return False
        return True

    #This will remove ALL of the dependant_entity_id's dependants as well
    def removeEntityDependancy(self, entity_id, dependant_entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            dependant_entity_status[DEPENDENT_ENTITIES_INDEX] = list()
            self._scene_handler.clearEntityDependancies(dependant_entity_id)
            try:
                entity_status[DEPENDENT_ENTITIES_INDEX].remove(dependant_entity_id)
                self._scene_handler.removeEntityDependancy(entity_id, dependant_entity_id)
            except:
                pass
            for current_dependant_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                try:
                    self._entity_status_lists[current_dependant_id][DEPENDENT_ENTITIES_INDEX].remove(dependant_entity_id)
                    self._scene_handler.removeEntityDependancy(current_dependant_id, dependant_entity_id)
                except:
                    pass
        except Exception as e:
            print("Exception caught: " + str(e))
            print("removeEntityDependancy(): ",entity_id, dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #This is not likely to change often, usually set once an entity is created if needed
    def setEntityAlwaysActive(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            #See if this is a change to the current status
            #If this attribute was already true, nothing else needs to change
            if not entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[ALWAYS_ACTIVE_INDEX] = True
                self._scene_handler.setAlwaysActive(entity_id)
                #call the dependant versions, because we do not want to recursively go through dependants list
                #when we _setDependantAlwaysActive(), they will call the methods on their own dependants
                if entity_status[ACTIVATED_INDEX]:
                    self._onscreen_entity_ids[entity_id] = True
                self._activateEntityPhysicsDependant(entity_id)
                self._activateEntityBehaviorDependant(entity_id)
                self._activateEntityAiDependant(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._setDependantAlwaysActive(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("setEntityAlwaysActive(): ",entity_id)
            return False
        return True

    #This only changes the passed in entity, not any of its dependants
    def _setDependantAlwaysActive(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            #See if this is a change to the current status
            #If this attribute was already true, nothing else needs to change
            if not dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[ALWAYS_ACTIVE_INDEX] = True
                self._scene_handler.setAlwaysActive(dependant_entity_id)
                if dependant_entity_status[ACTIVATED_INDEX]:
                    self._onscreen_entity_ids[dependant_entity_id] = True
                self._activateEntityPhysicsDependant(dependant_entity_id)
                self._activateEntityBehaviorDependant(dependant_entity_id)
                self._activateEntityAiDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_setDependantAlwaysActive(): ",dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #The scene handler will send the corresponding spriteoffscreen message if needed
    def removeEntityAlwaysActive(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already False, nothing else needs to change
            if entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[ALWAYS_ACTIVE_INDEX] = False
                self._scene_handler.removeAlwaysActive(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._removeEntityAlwaysActiveDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("removeEntityAlwaysActive(): ",entity_id)
            return False
        return True

    def _removeEntityAlwaysActiveDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already False, nothing else needs to change
            if dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[ALWAYS_ACTIVE_INDEX] = False
                self._scene_handler.removeAlwaysActive(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_removeEntityAlwaysActiveDependant(): ",dependant_entity_id)
            return False
        return True

    # This status would be set by game_engine, not by one of the entity components
    def setEntitySpriteVisible(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already true, nothing else needs to change
            if not entity_status[SPRITE_VISIBLE_INDEX]:
                entity_status[SPRITE_VISIBLE_INDEX] = True
                self._scene_handler.setSpriteVisible(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._setEntitySpriteDependantVisible(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("setEntitySpriteVisible(): ",entity_id)
            return False
        return True

    def _setEntitySpriteDependantVisible(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already true, nothing else needs to change
            if not dependant_entity_status[SPRITE_VISIBLE_INDEX]:
                dependant_entity_status[SPRITE_VISIBLE_INDEX] = True
                self._scene_handler.setSpriteVisible(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_setEntitySpriteDependantVisible(): ",dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #This is a more 'permanent' setting.  The entity will still exist in the scene grid, and
    #will be activated/deactivated if onscreen/offscreen.  It can still interact with other entities
    def setSpriteInvisible(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already False, nothing else needs to change
            if entity_status[SPRITE_VISIBLE_INDEX]:
                entity_status[SPRITE_VISIBLE_INDEX] = False
                self._scene_handler.setSpriteInvisible(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._setSpriteDependantInvisible(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("setSpriteInvisible(): ",entity_id)
            return False
        return True

    def _setSpriteDependantInvisible(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already False, nothing else needs to change
            if dependant_entity_status[SPRITE_VISIBLE_INDEX]:
                dependant_entity_status[SPRITE_VISIBLE_INDEX] = False
                self._scene_handler.setSpriteInvisible(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_setSpriteDependantInvisible(): ",dependant_entity_id)
            return False
        return True

    def setSpriteEthereal(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already False, nothing else needs to change
            if not entity_status[ETHEREAL_INDEX]:
                entity_status[ETHEREAL_INDEX] = True
                self._scene_handler.setSpriteEthereal(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._setSpriteDependantEthereal(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("setSpriteEthereal(): ", entity_id)
            return False
        return True

    def _setSpriteDependantEthereal(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already False, nothing else needs to change
            if not dependant_entity_status[ETHEREAL_INDEX]:
                dependant_entity_status[ETHEREAL_INDEX] = True
                self._scene_handler.setSpriteEthereal(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_setSpriteDependantEthereal(): ", dependant_entity_id)
            return False
        return True

    #Tangible is equivalent to NOT Ethereal
    def setSpriteTangible(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already true, nothing else needs to change
            if entity_status[ETHEREAL_INDEX]:
                entity_status[ETHEREAL_INDEX] = False
                self._scene_handler.setSpriteTangible(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._setSpriteDependantTangible(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("setSpriteTangible(): ", entity_id)
            return False
        return True

    #Tangible is equivalent to NOT Ethereal
    def _setSpriteDependantTangible(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already true, nothing else needs to change
            if dependant_entity_status[ETHEREAL_INDEX]:
                dependant_entity_status[ETHEREAL_INDEX] = False
                self._scene_handler.setSpriteTangible(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_setSpriteDependantTangible(): ", dependant_entity_id)
            return False
        return True

    # This status would be set by game_engine, not by one of the entity components
    # Notify physics component that an entity is active, if it is onscreen (or always active)
    def activateEntityPhysics(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already true, nothing else needs to change
            if not entity_status[PHYSICS_ACTIVE_INDEX]:# or entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[PHYSICS_ACTIVE_INDEX] = True
                #if entity_status[ACTIVATED_INDEX]:
                self._particle_component_system.activateParticle(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._activateEntityPhysicsDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("activateEntityPhysics(): ", entity_id)
            return False
        return True

    def _activateEntityPhysicsDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already true, nothing else needs to change
            if not dependant_entity_status[PHYSICS_ACTIVE_INDEX]:# or dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[PHYSICS_ACTIVE_INDEX] = True
                #if dependant_entity_status[ACTIVATED_INDEX]:
                self._particle_component_system.activateParticle(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_activateEntityPhysicsDependant(): ", dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #This is a more 'permanent' setting
    #'temporary' inactive due to sprite being offscreen set in the notify offScreen function
    def deactivateEntityPhysics(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already False, nothing else needs to change
            #not allowed to make physics inactive if always active is true
            if entity_status[PHYSICS_ACTIVE_INDEX] and not entity_status[ALWAYS_ACTIVE_INDEX]:
                #if entity_status[ACTIVATED_INDEX]: #don't send messages about deactivated entities
                self._particle_component_system.deactivateParticle(entity_id)
                entity_status[PHYSICS_ACTIVE_INDEX] = False
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._deactivateEntityPhysicsDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("deactivateEntityPhysics(): ", entity_id)
            return False
        return True

    def _deactivateEntityPhysicsDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already False, nothing else needs to change
            #not allowed to make physics inactive if always active is true
            if dependant_entity_status[PHYSICS_ACTIVE_INDEX] and not dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                #if dependant_entity_status[ACTIVATED_INDEX]: #don't send messages about deactivated entities
                self._particle_component_system.deactivateParticle(dependant_entity_id)
                dependant_entity_status[PHYSICS_ACTIVE_INDEX] = False
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_deactivateEntityPhysicsDependant(): ", dependant_entity_id)
            return False
        return True

    # This status would be set by game_engine, not by one of the entity components
    #Notify behavior component that an entity is active
    def activateEntityBehavior(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            if not entity_status[BEHAVIOR_ACTIVE_INDEX]:# or entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[BEHAVIOR_ACTIVE_INDEX] = True
                #if entity_status[ACTIVATED_INDEX]:
                self._behavior_component_system.activateBehaviorFSM(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._activateEntityBehaviorDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("activateEntityBehavior(): ", entity_id)
            return False
        return True

    def _activateEntityBehaviorDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            if not dependant_entity_status[BEHAVIOR_ACTIVE_INDEX]:# or dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[BEHAVIOR_ACTIVE_INDEX] = True
                #if dependant_entity_status[ACTIVATED_INDEX]:
                self._behavior_component_system.activateBehaviorFSM(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_activateEntityBehaviorDependant(): ", dependant_entity_id)
            return False
        return True

    #Notify behavior component that an entity is not active
    def deactivateEntityBehavior(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already False, nothing else needs to change
            #not allowed to make behavior inactive if always active is true
            if entity_status[BEHAVIOR_ACTIVE_INDEX] and not entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[BEHAVIOR_ACTIVE_INDEX] = False
                #if entity_status[ACTIVATED_INDEX]: #don't send messages about deactivated entities
                self._behavior_component_system.deactivateBehaviorFSM(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._deactivateEntityBehaviorDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("deactivateEntityBehavior(): ", entity_id)
            return False
        return True

    def _deactivateEntityBehaviorDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already False, nothing else needs to change
            #not allowed to make behavior inactive if always active is true
            if dependant_entity_status[BEHAVIOR_ACTIVE_INDEX] and not dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[BEHAVIOR_ACTIVE_INDEX] = False
                #if dependant_entity_status[ACTIVATED_INDEX]: #don't send messages about deactivated entities
                self._behavior_component_system.deactivateBehaviorFSM(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_deactivateEntityBehaviorDependant(): ", dependant_entity_id)
            return False
        return True

    #This status would be set by game_engine, not by one of the entity components
    #Notify AI component that an entity is active
    def activateEntityAi(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            if not entity_status[AI_ACTIVE_INDEX]:# or entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[AI_ACTIVE_INDEX] = True
                #if entity_status[ACTIVATED_INDEX]:
                self._ai_component_system.activateAiComponent(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._activateEntityAiDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("activateEntityAi(): ", entity_id)
            return False
        return True

    def _activateEntityAiDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            if not dependant_entity_status[AI_ACTIVE_INDEX]:# or dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[AI_ACTIVE_INDEX] = True
                #if dependant_entity_status[ACTIVATED_INDEX]:
                self._ai_component_system.activateAiComponent(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_activateEntityAiDependant(): ", dependant_entity_id)
            return False
        return True

    #Notify AI component that an entity is not active
    def deactivateEntityAI(self, entity_id):
        try:
            entity_status = self._entity_status_lists[entity_id]
            # If this attribute was already False, nothing else needs to change
            #not allowed to make ai inactive if always active is true
            if entity_status[AI_ACTIVE_INDEX] and not entity_status[ALWAYS_ACTIVE_INDEX]:
                entity_status[AI_ACTIVE_INDEX] = False
                #if entity_status[ACTIVATED_INDEX]: #don't send messages about deactivated entities
                self._ai_component_system.deactivateAiComponent(entity_id)
                for dependant_entity_id in entity_status[DEPENDENT_ENTITIES_INDEX]:
                    self._deactivateEntityAIDependant(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("deactivateEntityAI(): ", entity_id)
            return False
        return True

    def _deactivateEntityAIDependant(self, dependant_entity_id):
        try:
            dependant_entity_status = self._entity_status_lists[dependant_entity_id]
            # If this attribute was already False, nothing else needs to change
            #not allowed to make ai inactive if always active is true
            if dependant_entity_status[AI_ACTIVE_INDEX] and not dependant_entity_status[ALWAYS_ACTIVE_INDEX]:
                dependant_entity_status[AI_ACTIVE_INDEX] = False
                #if dependant_entity_status[ACTIVATED_INDEX]: #don't send messages about deactivated entities
                self._ai_component_system.deactivateAiComponent(dependant_entity_id)
        except Exception as e:
            print("Exception caught: " + str(e))
            print("_deactivateEntityAIDependant(): ", dependant_entity_id)
            return False
        return True

    #The scene handler calls this when an entity moves from offscreen to onscreen
    #This is not called on entities which are always active, but is called if they are invisible
    #entities which are'always active' already have physics and behavior active, this call not needed for them
    def notifySpriteOnScreen(self, entity_id):
        try:
            self._onscreen_entity_ids[entity_id] = True
        except:
            return False
        return True

    #The scene handler calls this when an entity moves from onscreen to offscreen
    #This is not called on entities which are always active, but is called if they are invisible
    def notifySpriteOffScreen(self, entity_id):
        try:
            del(self._onscreen_entity_ids[entity_id])
        except:
            return False
        return True

    #When this is added, we have set the entity status accoardingly in the other component systems
    #if sprite is found to be offscreen, and not offscreen active, than scene manager will send the update to EM
    def addEntityStatus(self,
                        entity_id,
                        active = True,
                        always_active = False,
                        sprite_visible = True,
                        sprite_ethereal = False,
                        physics_active = True,
                        behavior_active = True,
                        ai_active = True):
        self._entity_status_lists[entity_id] = [active,
                                                always_active,
                                                sprite_visible,
                                                sprite_ethereal,
                                                physics_active,
                                                behavior_active,
                                                ai_active,
                                                list()]#list is for dependant entity id's
        if active:
            self._onscreen_entity_ids[entity_id] = True

    def removeEntity(self, entity_id):
        try:
            #Remove this entity id from the list of dependants
            for dependant_entity_id in self._entity_status_lists[entity_id][DEPENDENT_ENTITIES_INDEX]:
                self._entity_status_lists[dependant_entity_id][DEPENDENT_ENTITIES_INDEX].remove(entity_id)
            del(self._entity_status_lists[entity_id])
            try:
                del(self._onscreen_entity_ids[entity_id])
            except:
                pass
        except Exception as e:
            print("Exception caught: " + str(e))
            print("removeEntity(): ", entity_id)
            return False
        return True

class EntitySceneManager:
    def __init__(self):
        self._active_entity_systems = dict() #{scene_id : EntityManager}
        self._entity_systems = dict() #{scene_id : EntityManager}
        # we will start with the first ID as 101 for now, keeping them as triple digists makes parsing logs easier
        self._next_id = 100
        #This stores every entity ID and can return it's scene/layer location when needed
        self._entity_scene_map = dict() #{entity_id : [scene_id, layer_id]})

    #Returns a list [scene_id, layer_id] for this entity.
    def getEntitySceneLayer(self, entity_id):
        return self._entity_scene_map[entity_id]

    def activateEntityManager(self, scene_id):
        try:
            self._active_entity_systems[scene_id] = self._entity_systems[scene_id]
        except Exception as e:
            print("Exception caught during activateEntityManager.activateEntityManager(): " + str(e))
            print("activateEntityManager(): ", scene_id)
            return False
        return True

    def deactivateEntityManager(self, scene_id):
        try:
            del(self._active_entity_systems[scene_id])
        except Exception as e:
            print("Exception caught: " + str(e))
            print("deactivateEntityManager(): ", scene_id)
            return False
        return True

    #Returns a unique/unused entity_id integer.
    #Starts from 1 and goes up, never is reset.  (Use a 64bit unsigned int)
    def generateEntityId(self):
        self._next_id+=1
        return self._next_id

    def addEntityManager(self, scene_id, entity_manager):
        self._entity_systems[scene_id] = entity_manager

    def removeEntityManager(self, scene_id, entity_ids):
        try:
            #if the entity is not active, the second delete throws an exception (which can be ignored)
            del(self._entity_systems[scene_id])
            del(self._active_entity_systems[scene_id])
        except:
            pass
        try:
            for entity_id in entity_ids:
                del(self._entity_scene_map[entity_id])
        except Exception as e:
            print(e)
            print("Exception caught deleting entity_id in EntitySceneManager.removeEntityManager")
            return False
        return True

    def addEntityStatus(self,
                        scene_id,
                        layer_id,
                        entity_id,
                        active = True,
                        always_active = False,
                        sprite_visible = True,
                        sprite_ethereal = False,
                        physics_active = True,
                        behavior_active = True,
                        ai_active = True):
        self._entity_systems[scene_id].addEntityStatus(entity_id,
                                                       active,
                                                       always_active,
                                                       sprite_visible,
                                                       sprite_ethereal,
                                                       physics_active,
                                                       behavior_active,
                                                       ai_active)
        self._entity_scene_map[entity_id] = [scene_id, layer_id]

    def removeEntity(self, entity_id, scene_id):
        self._entity_systems[scene_id].removeEntity(entity_id)
        del(self._entity_scene_map[entity_id])

    def activateEntity(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].activateEntity(entity_id)
        except:
            return False

    def deactivateEntity(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].deactivateEntity(entity_id)
        except:
            return False

    def addEntityDependancy(self, entity_id, dependant_entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].addEntityDependancy(entity_id, dependant_entity_id)
        except:
            return False

    def removeEntityDependancy(self, entity_id, dependant_entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].removeEntityDependancy(entity_id, dependant_entity_id)
        except:
            return False

    def setEntityAlwaysActive(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].setEntityAlwaysActive(entity_id)
        except:
            return False

    def removeEntityAlwaysActive(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].removeEntityAlwaysActive(entity_id)
        except:
            return False

    def setEntitySpriteVisible(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].setEntitySpriteVisible(entity_id)
        except:
            return False

    def setSpriteInvisible(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].setSpriteInvisible(entity_id)
        except:
            return False

    def setSpriteEthereal(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].setSpriteEthereal(entity_id)
        except:
            return False

    def setSpriteTangible(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].setSpriteTangible(entity_id)
        except:
            return False

    def activateEntityPhysics(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].activateEntityPhysics(entity_id)
        except:
            return False

    def deactivateEntityPhysics(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].deactivateEntityPhysics(entity_id)
        except:
            return False

    def activateEntityBehavior(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].activateEntityBehavior(entity_id)
        except:
            return False

    def deactivateEntityBehavior(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].deactivateEntityBehavior(entity_id)
        except:
            return False

    def activateEntityAi(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].activateEntityAi(entity_id)
        except:
            return False

    def deactivateEntityAI(self, entity_id, scene_id):
        try:
            return self._active_entity_systems[scene_id].deactivateEntityAI(entity_id)
        except:
            return False