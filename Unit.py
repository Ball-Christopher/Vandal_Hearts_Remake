import cocos

'''
CHRIS

Controls what happens when a unit wants to move/attack or pretty
much interact with the map layer or the user.
'''

import DefineGlobals


class Unit():

    def __init__(self,Sprite,Tile,Image,BG,P1,HP,MP,Move,Range,AT,DF,AGL):
        self.Sprite = Sprite
        self.Tile = Tile
        self.Image = Image
        self.bg = BG
        self.MoveRange = Move
        self.AttackRange = Range
        # Varaibles to record of the unit has moved or attacked.
        self.moved = False
        self.attacked = False
        # Variable to show if unit can be selected
        self.select = True
        # Variable so the unit knows which team it is on.
        self.P1 = P1
        # Variable for units that can pass through enemies.
        self.fly = False
        # Variables for the unit
        self.HP = HP
        self.MP = MP
        self.AT = AT
        self.DF = DF
        self.AGL = AGL
        self.label = cocos.text.Label(str(self.HP),font_name='Font_dark_size12.fnt',anchor_x="right",anchor_y="bottom")
        self.label.position = (self.Sprite.width/2,-self.Sprite.height/2)
        self.Sprite.add(self.label)
        pass

    def Hit(self,AtUnit):
        # Simple mechanics for now.
        self.HP -= (AtUnit.AT//2 - self.DF//6)
        self.Sprite.children = []
        self.label = cocos.text.Label(str(self.HP),font_name='Font_dark_size12.fnt',anchor_x="right",anchor_y="bottom")
        self.label.position = (self.Sprite.width/2,-self.Sprite.height/2)
        self.Sprite.add(self.label)
        if self.HP <= 0:
            DefineGlobals.unit_layer.remove(self.Sprite)

    def MoveUnit(self,x,y):
        # Moves the unit the number of tiles specified. Positive x right, positive y up.
        self.Sprite.position = (self.Sprite.position[0]+x*self.Tile.Cell.width,\
        self.Sprite.position[1]+y*self.Tile.Cell.height)
        # Fixes reference to tile
        self.Tile.hasUnit = False
        self.Tile.unit = None
        self.Tile = DefineGlobals.tileData[self.bg.get_key_at_pixel(self.Sprite.x,self.Sprite.y)]
        self.Tile.hasUnit = True
        self.Tile.unit = self
        self.moved = True

    def UnMoveUnit(self,x,y):
        # Moves the unit the number of tiles specified. Positive x right, positive y up.
        self.Sprite.position = (self.Sprite.position[0]+x*self.Tile.Cell.width,\
        self.Sprite.position[1]+y*self.Tile.Cell.height)
        # Fixes reference to tile
        self.Tile.hasUnit = False
        self.Tile.unit = None
        self.Tile = DefineGlobals.tileData[self.bg.get_key_at_pixel(self.Sprite.x,self.Sprite.y)]
        self.Tile.hasUnit = True
        self.Tile.unit = self
        self.moved = False

    def HighlightAvailable(self):
        ''' Naive implementation of Djikstra. A* may be quicker if needed. '''
        # Check that the unit can move
        if self.moved: return
        # Hightlight the available squares for the unit to move to.
        Q = [self.Tile.Cell]
        P = set()
        M = [self.MoveRange]
        while len(Q) > 0:
            Ind = M.index(max(M))
            Cell = Q.pop(Ind)
            MovLeft = M.pop(Ind)
            P.add(Cell)
            if MovLeft == 0: continue
            Temp = self.bg.get_neighbors(Cell)
            for C in Temp.values():
                if C is None or C in P or (not self.fly and DefineGlobals.tileData[C.i,C.j].hasUnit and
                                                   DefineGlobals.tileData[C.i,C.j].unit.P1!=DefineGlobals.P1Turn):
                    continue
                # Check that the current movement range is not higher...
                if C in Q:
                    M[Q.index(C)] = max(M[Q.index(C)], MovLeft - C.tile.properties['MovementCost'])
                    continue
                if MovLeft - C.tile.properties['MovementCost'] >= 0:
                    Q.append(C)
                    M.append(MovLeft - C.tile.properties['MovementCost'])
        for Cell in P:
            if DefineGlobals.tileData[Cell.i,Cell.j].hasUnit and Cell != self.Tile.Cell: continue
            self.bg.set_cell_color(Cell.i,Cell.j,(0,0,255))
            self.bg.set_cell_opacity(Cell.i,Cell.j,255)

    def HighlightAttack(self,Test=False):
        ''' Naive implementation of Djikstra. A* may be quicker if needed. '''
        # Hightlight the available squares for the unit to attack.
        Q = [self.Tile.Cell]
        P = set()
        M = [self.AttackRange]
        while len(Q) > 0:
            Ind = M.index(max(M))
            Cell = Q.pop(Ind)
            MovLeft = M.pop(Ind)
            P.add(Cell)
            if MovLeft == 0: continue
            Temp = self.bg.get_neighbors(Cell)
            for C in Temp.values():
                if C is None or C in P:
                    continue
                if Test:
                    # See if there is a unit that can be attacked here
                    if DefineGlobals.tileData[C.i,C.j].hasUnit and \
                                    DefineGlobals.tileData[C.i,C.j].unit.P1!=DefineGlobals.P1Turn:
                        return(True)
                # Check that the current movement range is not higher...
                if C in Q:
                    M[Q.index(C)] = max(M[Q.index(C)], MovLeft - 1)
                    continue
                if MovLeft - 1 >= 0:
                    Q.append(C)
                    M.append(MovLeft - 1)
        if Test: return(False)
        for Cell in P:
            if not DefineGlobals.tileData[Cell.i,Cell.j].hasUnit or \
                DefineGlobals.tileData[Cell.i,Cell.j].unit.P1==DefineGlobals.P1Turn: continue
            self.bg.set_cell_color(Cell.i,Cell.j,(255,0,0))
            self.bg.set_cell_opacity(Cell.i,Cell.j,255)

    def EndTurn(self):
        self.moved = False
        self.attacked = False
