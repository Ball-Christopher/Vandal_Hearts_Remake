import cocos
from cocos import tiles, layer

from MouseDisplay import MouseDisplay
from TileData import TileData
from Unit import Unit

'''
CHRIS

This script controls the game flow, creates the maps and populates with units
as appropriate.

Created the DefineGlobals class to hold the old global variables, which avoids
the circular dependencies which existed previously.
'''

import DefineGlobals

class Control:
    def __init__(self):
        self.main()
        pass

    def main(self):

        DefineGlobals.P1Turn = True

        DefineGlobals.Start()

        # Create a layer for the background.
        DefineGlobals.scroller = layer.ScrollingManager()
        # Create another layer for the units
        DefineGlobals.unit_layer = layer.ScrollableLayer()

        self.CreateTileMap()
        self.CreateUnits()

        # Create a scene for the map.
        main_scene = cocos.scene.Scene(DefineGlobals.scroller, MouseDisplay())
        DefineGlobals.AddQueue(main_scene)
        DefineGlobals.Pop()

    def CreateTileMap(self):

        # First load the file - This seems awfully slow...
        self.test_layer = tiles.load('Maps/Map-Ch1-St1.tmx')

        # Extract the background layer
        bg_layer = self.test_layer['Background']

        # Add background layer to the scroller.
        DefineGlobals.scroller.add(bg_layer)

        # Extract the properties into a dictionary
        tileDataArray = {}
        x = 0
        y = 0

        for col in bg_layer.cells:
            for cell in col:
                tileDataArray[x,y] = TileData(cell.position,cell.tile.properties['MovementCost'],cell.tile,cell)
                y += 1

            x += 1
            y = 0

        DefineGlobals.tileData = tileDataArray
        # Add the background layer as a permanent field
        DefineGlobals.bg = bg_layer



    def CreateUnits(self):
        P1 = True
        for Unit_Layer in (self.test_layer['Units_P1'], self.test_layer['Units_P2']):
            for Character in Unit_Layer.objects:
                # Get unit information
                UnitType = Character.name.split()[0]
                Dir = Character.properties['Dir']
                Dirmap = {'Up': '10', 'Down': '1', 'Left': '4', 'Right': '7'}
                # Create sprite for unit
                Image = 'Characters/' + UnitType + Dirmap[Dir] + '.png'
                unit = cocos.sprite.Sprite(Image)
                # Get the Tile which the unit is on
                x, y = Character.position
                # print(o.position,DefineGlobals.bg.get_key_at_pixel(x,y),UnitType)
                T = DefineGlobals.tileData[DefineGlobals.bg.get_key_at_pixel(x,y)]
                Tile = T.Cell
                # Put the unit in the correct position
                unit.position = (Character.position[0] + Tile.width // 2,
                                 Character.position[1] + Tile.height // 2)

                if P1:
                    Ch = DefineGlobals.Ch_Stats[UnitType]
                    Properties = {'HP': Ch.HP, 'MP': Ch.MP, 'Move': Ch.Move, 'AtkRng': Ch.AtkRng,
                                  'AT': Ch.AT, 'DF': Ch.DF, 'AGL': Ch.AGL}
                    # Create a Unit class, which can store the important information for each unit.
                    U = Unit(unit, T, Image, DefineGlobals.bg, P1, Properties)
                    pass
                else:
                    # Else read in from map information for player 2
                    U = Unit(unit, T, Image, DefineGlobals.bg, P1, Character.properties)
                    pass
                # Update the tile information to reflect unit
                T.hasUnit = True
                T.unit = U
                # Add unit to the unit layer.
                DefineGlobals.unit_layer.add(unit)
            P1 = False

        # Add unit layer to the scroller (make it visible...)
        DefineGlobals.scroller.add(DefineGlobals.unit_layer)


