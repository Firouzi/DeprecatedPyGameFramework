
#This simple class allows you to simulate the behavior of Pointers
#Use when you want multiple Classes to be able to watch an object, and one or both to modify it
class Ptr:
    def __init__(self,
                 obj, #Object
                 ptr_id, #int
                 free_callback): #func()
        #The class we are wrapping to treat as a "Pointer"
        self._obj = obj
        #Unique identifier given by the Ptr Pool handler
        self._ptr_id = ptr_id
        #This should notify the Ptr Pool that the Ptr is now freed
        self._free_callback = free_callback
        self._is_free = False

        #Once a Ptr is added to a scene layer, we don't need to re-add it.
        self._is_in_scene = False

    def isActive(self):
        return self._obj.isActive()

    def deactivate(self):
        return self._obj.deactivate() #no expected return val

    def activate(self):
        return self._obj.activate()  # no expected return val

    #get the obhect which is wrapped by this Ptr
    def get(self):
        assert(self._is_free == False) #We should never be getting a freed Ptr.obj
        return self._obj

    #Pass in the obj which will be wrapped by this Ptr
    def set(self, obj):
        assert(self._is_free == False) #We should never be setting a freed Ptr.obj
        self._obj = obj

    #"Free" the memory - marks this pointer as re-usable
    def free(self):
        if not self._is_free: #If we are already freed, do not continue
            self._is_free = True
            if self._free_callback is not None:
                self._free_callback(self._ptr_id)
            return True
        return False

    def isFree(self):
        return self._is_free

    #PtrPool calls this before returning the Ptr as available
    def reset(self):
        self._obj = None
        self._is_free = False

    def isInScene(self):
        return self._is_in_scene

    #when we add this component to the scene_layer, flag it as added
    #if already added it previously, scene layer doesn't need to re-add it.
    def setInScene(self,
                   is_in_scene = True):
        self._is_in_scene = is_in_scene



#So that a PTR can act a a renderable and clients don't need to know that they are Ptr's
#Acts as a PROXY for a renderable
class RenderablePtr(Ptr):
    def __init__(self,
                 obj, #Object - this will be the renderable instance
                 ptr_id, #int
                 free_callback): #func()
        Ptr.__init__(self, obj, ptr_id, free_callback)

    def getImage(self):
        return self._obj.getImage() #pygame.image

    #Tell the renderer to prepare it's image, coordinate and position values
    #The next calls will pull those values
    def calculateCoordinates(self,
                             camera_offset, #[int, int]
                             lag_normalized): #float [0,1)
        self._obj.calculateCoordinates(camera_offset = camera_offset,
                                       lag_normalized = lag_normalized)

    #return the portion(s) of the image to draw.
    #should be in sets of 4 ints, x,y,width,height
    def getImageCoordinates(self):
        return self._obj.getImageCoordinates() #[int]

    def getTilePosition(self):
        return self._obj.getTilePosition() #[int, int, int]

    def getWorldCoordinates(self):
        return self._obj.getWorldCoordinates() #[int, int, int]

    #The x,y,z position of the renderable
    #returned in groups of 3
    def getScreenCoordinates(self):
        return self._obj.getScreenCoordinates() #[int, int, int]

    #Adjusted position to where the renderable should be shown to touch ground (for sorting)
    def getGroundPositionPx(self):
        return self._obj.getGroundPositionPx() #[int, int, int]

    ###SPRITE FUNCTIONS###

    def updateBehaviorState(self, behavior_state):
        return self._obj.updateBehaviorState(behavior_state) #no expected return val


#Sends blank pointers to use for SceneComponents.  Tracks which pointers
#Are currently in use, and which are free.  Re-uses Ptrs that have been freed
#TODO - not necessarily better to always reuse a PTR
#TODO - only reuse if the other option is allocate?  Set a threshold for when to reuse vs when to send new?
class PtrPool:
    def __init__(self,
                 pool_size = 100): #number of Ptr's to allocate
        self._pool_size = pool_size

        self._ptr_class_type = None #We change this based on the type of PtrPool we are managing
        self._ptr_pool = None
        self._initializePtrPool()

        self._next_id = 0
        self._free_ids = list() #track ID's that have been freed

    #We can override this method in PtrPool Child classes, changing the types of Ptrs that will be created
    def _setPtrType(self):
        self._ptr_class_type = Ptr

    def _initializePtrPool(self):
        self._setPtrType()
        self._ptr_pool = list()
        count = 0
        while count < self._pool_size:
            self._ptr_pool.append(self._ptr_class_type(obj = None,
                                                       ptr_id = count,
                                                       free_callback = self.freed))
            count+=1
        self._ptr_pool = tuple(self._ptr_pool)

    #Call this if a Ptr is requested and none are available
    #Doubls the amount of available Ptrs
    #We hope not to use this function!  allocate enough Ptrs to begin with
    def _allocate(self):
        self._ptr_pool = list(self._ptr_pool)
        count = self._pool_size
        max = self._pool_size*2
        while count < max:
            self._ptr_pool.append(self._ptr_class_type(obj = None,
                                                       ptr_id = count,
                                                       free_callback = self.freed))
            count+=1
        self._ptr_pool = tuple(self._ptr_pool)
        self._pool_size = max

    #Has been notified that a Ptr is no longer in use
    def freed(self,
              ptr_id):
        self._free_ids.append(ptr_id)

    #returns either new or recycled Ptr
    #TODO - it may be more efficient to only return freed pointers when there are none left to allocate
    def requestPtr(self):
        if len(self._free_ids) > 0:
            free_id = self._free_ids.pop()
            self._ptr_pool[free_id].reset()
            return self._ptr_pool[free_id]
        else:
            if self._next_id == self._pool_size:
                self._allocate()
            self._next_id += 1
            return self._ptr_pool[self._next_id - 1]

class RenderablePtrPool(PtrPool):
    def __init__(self,
                 pool_size = 100):
        super(RenderablePtrPool, self).__init__(pool_size=pool_size)

    def _setPtrType(self):
        self._ptr_class_type = RenderablePtr


#For unit testing
if __name__ == "__main__":
    print("Testing Ptrs begin")
    class A: #dummy class for testing
        def __init__(self, data):
            self.data = data

    ptr_pool = PtrPool(pool_size = 3)
    ptrs = list()
    ptr1 = ptr_pool.requestPtr()

    ptr1.set(A(5))
    ptrs.append(ptr1)
    print(ptrs[0].get().data)

    ptr1.set(A(3))
    print(ptrs[0].get().data)

    ptr2 = ptr_pool.requestPtr()
    ptr2.set(A(100))
    ptrs.append(ptr2)

    ptr3 = ptr_pool.requestPtr()
    ptr3.set(A(2030))
    ptrs.append(ptr3)

    ptr4 = ptr_pool.requestPtr()
    ptr4.set(A(-4))
    ptrs.append(ptr4)

    ptrs[1].free()

    ptr5 = ptr_pool.requestPtr()
    ptr5.set(A(-5000))

    ptr6 = ptr_pool.requestPtr()
    ptr6.set(A(-100))

    ptr5.free()
    ptr5.free()
    ptr5.free()

    ptr7 = ptr_pool.requestPtr()
    ptr7.set(A(-900))

    for ptr in ptrs:
        ptr.free()

    ptr1 = ptr_pool.requestPtr()
    ptr2 = ptr_pool.requestPtr()
    ptr3 = ptr_pool.requestPtr()
    ptr4 = ptr_pool.requestPtr()

    ptr2.set(A(22384))
    print("Testing Ptrs end")









