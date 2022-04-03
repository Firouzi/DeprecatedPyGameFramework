import sqlite3 as SQ3
import pickle
import json

DB = 'C:\\Users\\Robert\\Desktop\\repositories\\GameDev\\PythonGameDevelopment\\swordFightProto\\dir_database\\db_CharmQuark.sqlite'

TYPE_INT = 'INTEGER'
TYPE_TEXT = 'TEXT'
TYPE_BLOB = 'BLOB'

### LEVEL TABLE ###
table_LevelData = 'Levels'
col_levelIndex = 'level_index' #primary key
col_name = 'name' 
col_height = 'height' #int
col_width = 'width' #int
col_lower_tiles = 'lower_tiles' #list of integers which will be converted to coordinates in pygame
col_upper_tiles = 'upper_tiles' #list of integers which will be converted to coordinates in pygame
col_borders = 'borders' #list

### TILEMAP TABLE ###
table_TileMaps = 'TileMaps' 
col_tileIndex = 'tilemap_index' #primary key
col_levelKey = 'level_key'
col_filepath = 'file_path'
col_tileSize = 'tile_size'
#col height, in tiles
#col width, in tiles
col_tileType = 'tileType' #eg lower, upper...

### LEVELEVENTS TABLE ###
table_LevelEvents = 'LevelEvents'
# col_levelKey = 'level_key'

### GAMEEVENTS TABLE ###
table_GameEvents = 'GameEvents'
# col_levelKey = 'level_key'

### ACTORS TABLE ###
table_Actors = 'Actors'
# col_levelKey = 'level_key'

### BACKGROUNDS TABLE ###
table_Backgrounds = 'Backgrounds'
col_backgroundsIndex = 'background_index' #primary key
# col_levelKey = 'level_key'
# col_filepath = 'file_path'
col_px_height = 'pxHeight' 
col_px_width = 'pxWidth'  
col_visibile_sections = 'visibleSections'
col_scrolling = 'scrolling'
col_alpha = 'alpha'
col_layer = 'layer' #int to determine layer, 0 is bottom layer

### FOREGROUNDS TABLE ###
table_Foregrounds = 'Foregrounds'
col_foregroundsIndex = 'foreground_index' #primary key
# col_levelKey = 'level_key'
# col_filepath = 'file_path'
# col_height = 'height' - pixels
# col_width = 'width'  - pixels
# col_layer = 'layer' #int to determine layer, 0 is bottom layer
# col_px_height = 'pxHeight' 
# col_px_width = 'pxWidth'  
# col_visibile_sections = 'visibleSections'
# col_scrolling = 'scrolling'
# col_alpha = 'alpha'
# col_layer = 'layer' #int to determine layer, 0 is bottom layer

#columNames should be a string of comma seperated column names 
#data should be a string of comma seperated values
def addRow(db, table, columNames, data):
	query = "INSERT INTO {} ({}) VALUES ({})".format(table, columNames, data)
	print(query)
	conn = SQ3.connect(db)
	try:
		conn.execute(query)
	except Exception as e:
		print('Exception caught: ' +str(e))
		
	conn.commit()
	conn.close()

def addColumn(db, table, col, type):
	query = "ALTER TABLE {} ADD COLUMN '{}' {}".format(table, col, type)
	
	conn = SQ3.connect(db)
	conn.execute(query)
	conn.commit()
	conn.close()

#creates a table with 1 column (as the primary key if true)
def createTable(db, table, col, type, primaryKey = True):
	if primaryKey:
		query = 'CREATE TABLE {} ({} {} PRIMARY KEY)'.format(table, col, type)
	else:
		query = 'CREATE TABLE {} ({} {})'.format(table, col, type)		
	conn = SQ3.connect(db)
	conn.execute(query)
	conn.commit()
	conn.close()

def addLevelDataRow(name='level_', height=10, width=10, lower_tiles = [], upper_tiles=[], borders=[]):
    colNames = 'name, height, width, lower_tiles, upper_tiles, borders'
    data = '"'+str(name)+'",'+str(height)+',"'+str(width)+'","'+str(lower_tiles)+'","'+str(upper_tiles)+'","'+str(borders)+'"'
    addRow(DB, table_LevelData, colNames, data)
	
#Builds all tables for CharmQuark database
def createDatabase():
	setupLevelDataTable()
	setupTilemapTable()
	setupBackgroundsTable()
	setupForegroundsTable()	
	setupLevelEventsTable()
	setupGameEventsTable()	
	setupActorsTable()	

def setupActorsTable():
	createTable(DB, table_Actors, col_levelKey, TYPE_INT, False)	

def setupForegroundsTable():
	createTable(DB, table_Foregrounds, col_foregroundsIndex, TYPE_INT)
	addColumn(DB, table_Foregrounds, col_levelKey, TYPE_INT)	
	addColumn(DB, table_Foregrounds, col_filepath, TYPE_TEXT)	
	addColumn(DB, table_Foregrounds, col_px_height, TYPE_INT)	
	addColumn(DB, table_Foregrounds, col_px_width, TYPE_INT)	
	addColumn(DB, table_Foregrounds, col_visibile_sections, TYPE_BLOB)
	addColumn(DB, table_Foregrounds, col_scrolling, TYPE_BLOB)
	addColumn(DB, table_Foregrounds, col_alpha, TYPE_INT)
	addColumn(DB, table_Foregrounds, col_layer, TYPE_INT)
	
def setupBackgroundsTable():
	createTable(DB, table_Backgrounds, col_backgroundsIndex, TYPE_INT)
	addColumn(DB, table_Backgrounds, col_levelKey, TYPE_INT)	
	addColumn(DB, table_Backgrounds, col_filepath, TYPE_TEXT)	
	addColumn(DB, table_Backgrounds, col_px_height, TYPE_INT)	
	addColumn(DB, table_Backgrounds, col_px_width, TYPE_INT)	
	addColumn(DB, table_Backgrounds, col_visibile_sections, TYPE_BLOB)
	addColumn(DB, table_Backgrounds, col_scrolling, TYPE_BLOB)
	addColumn(DB, table_Backgrounds, col_alpha, TYPE_INT)
	addColumn(DB, table_Backgrounds, col_layer, TYPE_INT)		

	
def setupGameEventsTable():
	createTable(DB, table_GameEvents, col_levelKey, TYPE_INT, False)
	
def setupLevelEventsTable():
	createTable(DB, table_LevelEvents, col_levelKey, TYPE_INT, False)	
	
def setupTilemapTable():
	createTable(DB, table_TileMaps, col_tileIndex, TYPE_INT)
	addColumn(DB, table_TileMaps, col_levelKey, TYPE_INT)		
	addColumn(DB, table_TileMaps, col_filepath, TYPE_TEXT)
	addColumn(DB, table_TileMaps, col_tileSize, TYPE_INT)
	addColumn(DB, table_TileMaps, col_height, TYPE_INT)
	addColumn(DB, table_TileMaps, col_width, TYPE_INT)
	addColumn(DB, table_TileMaps, col_tileType, TYPE_TEXT)
	
def setupLevelDataTable():
	createTable(DB, table_LevelData, col_levelIndex, TYPE_INT)
	addColumn(DB, table_LevelData, col_name, TYPE_TEXT)	
	addColumn(DB, table_LevelData, col_height, TYPE_INT)	
	addColumn(DB, table_LevelData, col_width, TYPE_INT)	
	addColumn(DB, table_LevelData, col_lower_tiles, TYPE_BLOB)	
	addColumn(DB, table_LevelData, col_upper_tiles, TYPE_BLOB)	
	addColumn(DB, table_LevelData, col_borders, TYPE_BLOB)		
	
def getLevel(index):
	query = "SELECT * FROM Levels WHERE level_index = {}".format(index)
	
	conn = SQ3.connect(DB)
	try:
		table = conn.execute(query)
	except Exception as e:
		print('Exception caught: ' +str(e))
		
	for row in table:
		tiles = json.loads(row[4])
	print(tiles)
	print()
	print(tiles[0])
	print()
	print(tiles[0][0])
		
		
	conn.close()	
	
# createDatabase()
# addLevelDataRow('addTest3', 20,24,pickle.dumps([1,0,1,5,1]),pickle.dumps([0,2,3,0,0]),pickle.dumps([3,56,7,7,12]))
#TODO, query the DB
# getLevel(1)

# lowt = list(pickle.dumps([[1,2,3],[4,5,6],[7,8,9]]))
# hit = pickle.dumps([[1,2,3],[4,5,6],[7,8,9]])
# bar = pickle.dumps([[1,2,3],[4,5,6],[7,8,9]])

# query = "INSERT INTO Levels (name, height, width, lower_tiles, upper_tiles, borders) VALUES ('blobtest', 10, 10, {}, {}, {})"\
# .format(SQ3.Binary(lowt), SQ3.Binary(hit), SQ3.Binary(bar))
# print(query)
# conn = SQ3.connect(DB)
# conn.execute(query)
# conn.commit()
# conn.close()