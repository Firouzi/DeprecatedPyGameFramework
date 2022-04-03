"""
Example code for how to handle tracking the number of active clones belong to a sprite.
When a clone is activated/deactivated, it needs to send a message to the original
If the original is notified an no clones or itself are active, it can deactivate the entity
"""

class Sprite:
	CLONES = list() 
	def __init__(self, data):
		self.data = data
		self.is_active = True
		self.v_clone = None
		self.h_clone = None
		self.active_clones = 0
		Sprite.CLONES.append(self)
		
	def cloneActivated(self):
		self.active_clones+=1
	
	def cloneDeactivated(self):
		self.active_clones-=1
		
	def createHClone(self, data):
		if self.h_clone is None:
			self.h_clone = HClone(data, self)

	def createVClone(self, data):
		if self.v_clone is None:
			self.v_clone = VClone(data, self)
	
	def deactivate(self):
		self.is_active = False

	def activate(self):
		self.is_active = True
		
class HClone(Sprite):
	def __init__(self, data, original):
		super(HClone, self).__init__(data)
		self.original = original
		self.original.cloneActivated()

	def createHClone(self, data):
		if self.h_clone is None:
			self.h_clone = HClone(data, self.original)

	def createVClone(self, data):
		if self.v_clone is None:
			self.v_clone = VClone(data, self.original)		
		
	def deactivate(self):
		if self.is_active:
			self.is_active = False
			self.original.cloneDeactivated()

	def activate(self):
		if not self.is_active:
			self.is_active = True
			self.cloneActivated()
		
class VClone(HClone):
	def __init__(self, data, original):
		super(VClone, self).__init__(data, original)

	def createHClone(self, data):
		pass #Vclones can only create VClones	
		
	def createVClone(self, data):
		if self.v_clone is None:
			self.v_clone = VClone(data, self.original)		