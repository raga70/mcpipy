import mcpi.minecraft as minecraft
import mcpi.block as block
import sys, random
from math import *
from random import randint as rand
from random import shuffle
import server
from mcpi.vec3 import Vec3

class MazeChestGenerator:
	
	def __init__(self, worldSpawn_vec3):
		self.spawnX = worldSpawn_vec3.x
		self.spawnY = worldSpawn_vec3.y
		self.spawnZ = worldSpawn_vec3.z
		
		self._defineLoot()
	#eof init
	
	
	def setRange(self, vec3_from, vec3_to):
		#avoid chests on maze bounding walls
		self.minX = min(vec3_from.x+1, vec3_to.x+1)
		self.minZ = min(vec3_from.z+1, vec3_to.z+1)
		self.maxX = max(vec3_from.x-1, vec3_to.x-1)
		self.maxZ = max(vec3_from.z-1, vec3_to.z-1)
		
		assert vec3_from.y == vec3_to.y, "provide two corner points on the same Y level"
		self.y_level = vec3_to.y + 1 # one above the floor
		
		#randomization optimization
		self._pairs = []
		for i in range(self.minX, self.maxX):
			for j in range(self.minZ, self.maxZ):
				self._pairs.append((i, j))
		shuffle(self._pairs)
		
	#eof setRange
	
	
	def placeChests(self, num_chests, lootItemsPerChest):
		
		# Connect to Minecraft.
		try:
			mc = minecraft.Minecraft.create(server.address)
		except:
			print "Cannot connect to Minecraft."
			sys.exit(0)
		
		chests = 0
		
		while chests < num_chests and len(self._pairs) > 0:
			randpos = self._pairs.pop(0)
			randX = randpos[0]
			randZ = randpos[1]
			
			corridors = 0
			diagonals = 0
			
			if mc.getBlock(randX, self.y_level, randZ) == block.AIR.id or mc.getBlock(randX, self.y_level, randZ) == block.CHEST_TRAPPED.id:
				print ".",
				#print "checked %s, %s, %s - not our case"%(randX, self.y_level, randZ)
				continue
			
			"""find the end of a wall, air at exactly three of the sides
			while searching find the direction of the wall"""
			if mc.getBlock(randX, self.y_level, randZ+1) == block.AIR.id:
				corridors += 1	
			else: 
				direction = 0x2 #0x2: Facing north (for ladders and signs, attached to the north side of a block)
			if mc.getBlock(randX-1, self.y_level, randZ) == block.AIR.id:
				corridors += 1	
			else: 
				direction = 0x5 #0x5: Facing east
			if mc.getBlock(randX, self.y_level, randZ-1) == block.AIR.id:
				corridors += 1	
			else: 
				direction = 0x3 #0x3: Facing south
			if mc.getBlock(randX+1, self.y_level, randZ) == block.AIR.id:
				corridors += 1	
			else: 
				direction = 0x4 #0x4: Facing west

			if mc.getBlock(randX+1, self.y_level, randZ+1) == block.AIR.id:
				diagonals += 1
			if mc.getBlock(randX+1, self.y_level, randZ-1) == block.AIR.id:
				diagonals += 1
			if mc.getBlock(randX-1, self.y_level, randZ+1) == block.AIR.id:
				diagonals += 1
			if mc.getBlock(randX-1, self.y_level, randZ-1) == block.AIR.id:
				diagonals += 1


			if corridors == 3 and diagonals == 4:
				mc.setBlock(randX, self.y_level+1, randZ, block.AIR.id)
				mc.setBlock(randX, self.y_level, randZ, block.CHEST_TRAPPED.id, direction) 
				chests += 1
				print "\n"
				print ("chest N%s(of %s) at /tp %s %s %s -> %s" % (chests, num_chests, randX+self.spawnX, self.y_level+self.spawnY-1, randZ+self.spawnZ, self._getChestContents(lootItemsPerChest)))
		#eof while
		
	#eof placeChests
	
	
	
	def _getChestContents(self, numLootItems):
		
		lootStr = "["
		
		for i in range(numLootItems):
			lootStr += self._getLootItem()
			lootStr += ", "
			
		lootStr += "]"
		return lootStr
	
	#eof _chestContents
	
	def _getLootItem(self):
		res = self.loot.pop(0)
		return res
	#eof getLootItem
	
	def _defineLoot(self):
		"""
		Define maximum items of a kind to be spread in the chests.
		"""
		
		self._lootDef = (
			("rotten_flesh",				100),
			("Bone",								60),
			("Gunpowder",						50),
			("Iron_Ingot",					45),
			("Gold_Ingot",					25),
			
			("Gold_Helmet",					25),
			("Gold_Chestplate", 		25),
			("Gold_Leggings",				25),
			("Gold_Boots",					25),
			("Chainmail_Helmet",		15),
			("Chainmail_Chestplate", 15),
			("Chainmail_Leggings",	15),
			("Chainmail_Boots",			15),
			("Gold_Sword",					22),
			("Iron_Sword",					18),
			("Diamond_Sword",				6),
			
			("Name_Tag",						18),
			("Saddle",							18),
			("Obsidian", 						36),
			
			("Diamond",							18),
			("Iron_Barding",				9),
			("Gold_Barding", 				8),
			("Diamond_Barding", 		6),

			("Golden_Apple",				6),
			("Enchanted_Book",			6),				
		)
		
		self.loot = []
		for pair in self._lootDef:
			print "/give Admin %s %s" % (pair[0], pair[1])
			self.loot.extend([ pair[0] ] * pair[1] ) # e.g ["tag"] * 6 
		#eof for
		
		shuffle(self.loot)
		
		print "==eof def loot=="
	#eof defineLoot()
	
#eof class

