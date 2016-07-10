import cocos

import DG
from Utilities import In_Range, Find_Path_To_Nearest_Enemy, Resolve_Attack


class Unit:
    def __init__(self, Sprite, Tile, UnitType, BG, P1, Properties):
        self.Sprite = Sprite
        self.Tile = Tile
        self.UnitType = UnitType
        self.bg = BG
        self.MoveRange = Properties['Move']
        self.AttackRange = Properties['AtkRng']
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
        self.HP = Properties['HP']
        self.Max_HP = Properties['HP']
        self.MP = Properties['MP']
        self.AT = Properties['AT']
        self.DF = Properties['DF']
        self.AGL = Properties['AGL']
        self.Direction = Properties['Direction']
        self.Update_Label()
        pass

    def Update_Label(self):
        Black = cocos.sprite.Sprite('Resources/black.png', anchor=(50, 400))
        Black.scale_x = 24 / 100
        Black.scale_y = 4 / 100
        if self.P1:
            Health = cocos.sprite.Sprite('Resources/green.png', anchor=(50, 400))
            Health.scale_x = self.HP / self.Max_HP * 24 / 100
            Health.scale_y = 4 / 100
            Health.position = Health.position[0] - (1 - self.HP / self.Max_HP) / 2 * 24, Health.position[1]
            pass
        else:
            Health = cocos.sprite.Sprite('Resources/red.png', anchor=(50, 400))
            Health.scale_x = self.HP / self.Max_HP * 24 / 100
            Health.scale_y = 4 / 100
            Health.position = Health.position[0] - (1 - self.HP / self.Max_HP) / 2 * 24, Health.position[1]
            pass
        self.Sprite.add(Black)
        self.Sprite.add(Health)

    def Hit(self, AtUnit):
        # Add concept of direction.
        if self.Direction == AtUnit.Direction:
            Direction_Bonus = 1.5
        elif (self.Direction, AtUnit.Direction) in (
        ('Left', 'Right'), ('Right', 'Left'), ('Up', 'Down'), ('Down', 'Up')):
            Direction_Bonus = 1
        else:
            Direction_Bonus = 1.25
        self.HP -= round(AtUnit.AT // 2 * Direction_Bonus - self.DF // 6, 0)
        self.Sprite.children = []
        self.Update_Label()
        if self.HP <= 0:
            DG.unit_layer.remove(self.Sprite)

    def MoveUnit(self, x, y, Unmove=False, Debug='') -> None:
        # Moves the unit the number of tiles specified. Positive x right, positive y up.
        self.Sprite.position = (self.Sprite.position[0] + x * self.Tile.Cell.width,
                                self.Sprite.position[1] + y * self.Tile.Cell.height)
        # Fixes reference to tile
        self.Tile.Remove_Unit()
        self.Tile = DG.tileData[self.bg.get_key_at_pixel(self.Sprite.x, self.Sprite.y)]
        if Debug != '': print(Debug, self.bg.get_key_at_pixel(self.Sprite.x, self.Sprite.y))
        self.Tile.Add_Unit(self)
        if Unmove:
            self.moved = False
        else:
            self.moved = True

    def HighlightAvailable(self, Colour=(0, 0, 255)) -> None:
        # Check that the unit can move
        if self.moved: return
        # Highlight the available squares for the unit to move to.
        P = In_Range(self.Tile.Cell, self.MoveRange, self, lambda x: x.tile.properties['MovementCost'],
                     lambda C, P, Unit: C is None or
                                        C in P or
                                        (not Unit.fly and
                                         DG.tileData[C.i, C.j].hasUnit and
                                         DG.tileData[C.i, C.j].unit.P1 != DG.P1Turn))
        for Cell in P:
            if DG.tileData[Cell.i, Cell.j].hasUnit and Cell != self.Tile.Cell: continue
            self.bg.set_cell_color(Cell.i, Cell.j, Colour)
            self.bg.set_cell_opacity(Cell.i, Cell.j, 255)

    def HighlightAttack(self, Test=False, Colour=(255, 0, 0)):
        # Highlight the available squares for the unit to attack.
        if Test:
            return In_Range(self.Tile.Cell, self.AttackRange, self, lambda x: 1,
                            lambda C, P, Unit: C is None or C in P,
                            Test_Fun=lambda C: DG.tileData[C.i, C.j].hasUnit and
                                               DG.tileData[C.i, C.j].unit.P1 != DG.P1Turn)
        else:
            P = In_Range(self.Tile.Cell, self.AttackRange, self,
                         lambda x: 1, lambda C, P, Unit: C is None or C in P)
        for Cell in P:
            if not DG.tileData[Cell.i, Cell.j].hasUnit or \
                            DG.tileData[Cell.i, Cell.j].unit.P1 == DG.P1Turn: continue
            self.bg.set_cell_color(Cell.i, Cell.j, Colour)
            self.bg.set_cell_opacity(Cell.i, Cell.j, 255)

    def EndTurn(self) -> None:
        self.moved = False
        self.attacked = False

    def Zombie(self) -> None:
        # Start by attacking if possible.
        P = In_Range(self.Tile.Cell, self.MoveRange, self,
                     lambda x: x.tile.properties['MovementCost'],
                     lambda C, P, Unit: C is None or
                                        C in P or
                                        (not self.fly and
                                         DG.tileData[C.i, C.j].hasUnit and
                                         DG.tileData[C.i, C.j].unit.P1 != DG.P1Turn))
        for Cell in P:
            New_Cell = DG.tileData[Cell.i, Cell.j]
            if New_Cell.hasUnit and Cell != self.Tile.Cell: continue
            Enemy_Cell = self.Enemy_In_Range(Cell)
            if Enemy_Cell is not None:
                # Move unit to this square
                self.MoveUnit(Cell.i - self.Tile.Cell.i, Cell.j - self.Tile.Cell.j)
                # Clear out the attacking logic.
                Resolve_Attack((Cell.i, Cell.j), (Enemy_Cell.i, Enemy_Cell.j))
                return
        # Getting here implies that there are no enemies in range.  Now we move.
        self.Move_Towards_Closest_Enemy()


    def Enemy_In_Range(self, Cell):
        P = In_Range(Cell, self.AttackRange, self,
                     lambda x: 1,
                     lambda C, P, Unit: C is None or C in P,
                     Break_Fun=lambda C: DG.tileData[C.i, C.j].hasUnit and
                                         DG.tileData[C.i, C.j].unit.P1 != DG.P1Turn)
        return P

    def Move_Towards_Closest_Enemy(self) -> None:
        """
        Finds the closest enemy (relative to this unit) and moves towards them.  May not necessarily
        be an optimal path if the movement cost is greater than 1 and there are multiple shortest paths.
        No explicit tie-breaking is done when more than one closest unit is present.

        10/07/2016: Modified to not land on a cell which is already inhabited.
        :return:
        """
        Path = Find_Path_To_Nearest_Enemy(self.Tile.Cell)
        if Path is None: return
        # Go down the path until the movement range runs out.
        Move_Left = self.MoveRange
        while Move_Left >= Path[-1].tile.properties['MovementCost']:
            Next_Cell = Path.pop()
            Move_Left -= Next_Cell.tile.properties['MovementCost']
            if DG.tileData[Next_Cell.i, Next_Cell.j].hasUnit: continue
            Move_Cell = Next_Cell.i, Next_Cell.j
        # Move the unit to this cell
        try:
            self.MoveUnit(Move_Cell[0] - self.Tile.Cell.i, Move_Cell[1] - self.Tile.Cell.j)
        except NameError:
            return
