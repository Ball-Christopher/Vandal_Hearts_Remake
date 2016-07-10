import pyglet

import DG


def Set_Image(Unit, Image):
    image = pyglet.resource.image(Image)
    Unit.Sprite._set_image(image)


def Get_Direction(Attack_Unit, Defend_Unit):
    Attack_Cell = Attack_Unit.Tile.Cell
    Defend_Cell = Defend_Unit.Tile.Cell
    x_diff, y_diff = Attack_Cell.i - Defend_Cell.i, Attack_Cell.j - Defend_Cell.j
    if abs(x_diff) <= abs(y_diff) and y_diff > 0: return ('Down')
    if abs(x_diff) <= abs(y_diff) and y_diff < 0: return ('Up')
    if abs(x_diff) > abs(y_diff) and x_diff > 0: return ('Left')
    if abs(x_diff) > abs(y_diff) and x_diff < 0: return ('Right')


def Resolve_Attack(Attacking_Cell, Defending_Cell):
    """
    Resolves an attack between two units.
    :param Attacking_Cell: 2D Tuple with Cell coordinates of attacking unit.
    :param Defending_Cell: 2D Tuple with Cell coordinates of defending unit.
    :return: None.
    """
    AtUnit = DG.tileData[Attacking_Cell].unit
    DfUnit = DG.tileData[Defending_Cell].unit
    Dirmap = {'Up': '10', 'Down': '1', 'Left': '4', 'Right': '7'}
    Direction = Get_Direction(AtUnit, DfUnit)
    Image = 'Characters/' + AtUnit.UnitType + Dirmap[Direction] + '.png'
    Set_Image(AtUnit, Image)
    DfUnit.Hit(AtUnit)
    if DfUnit.HP <= 0:
        # Kill the unit, or at least make it disappear
        DG.tileData[Defending_Cell].unit = None
        DG.tileData[Defending_Cell].hasUnit = False
        return
    # Turn towards attacker even if you can't counter.
    Direction = Get_Direction(DfUnit, AtUnit)
    Image = 'Characters/' + DfUnit.UnitType + Dirmap[Direction] + '.png'
    Set_Image(DfUnit, Image)
    if abs(Attacking_Cell[0] - Defending_Cell[0]) + abs(Attacking_Cell[1] - Defending_Cell[1]) <= DfUnit.AttackRange:
        AtUnit.Hit(DfUnit)
        if AtUnit.HP <= 0:
            # Kill the unit, or at least make it disappear
            DG.tileData[Attacking_Cell].unit = None
            DG.tileData[Attacking_Cell].hasUnit = False


def In_Range(Start, Value, Unit, Dist_Fun, Update_Condition,
             Test_Fun=None, Break_Fun=None):
    """
    Finds all squares within Value squares of Start.  Allows for flexible distance functions,
    update conditions (such as not passing movement through enemies) and terminating conditions.
    :param Start: Starting cell
    :param Value: Number of cells to search
    :param Unit: Reference to unit
    :param Dist_Fun: A function which takes a cell as an argument and returns a distance
    :param Update_Condition: A function of the Cell, Unit and the set of cells already searched which returns a
    boolean which determines if the Cell is included.
    :param Test_Fun: Allows for testing if a cell meeting conditions is in range. Returns a boolean.
    :param Break_Fun: Similar to test function except it returns the Cell or None.
    :return: Either a list of cells in range, an indicator of if a particular cell is in range or a cell which meets
    certain conditions.
    """
    Q = [Start]
    P = set()
    M = [Value]
    while len(Q) > 0:
        Ind = M.index(max(M))
        Cell = Q.pop(Ind)
        MovLeft = M.pop(Ind)
        P.add(Cell)
        if Break_Fun is not None and Break_Fun(Cell):
            return Cell
        if MovLeft == 0: continue
        Temp = DG.bg.get_neighbors(Cell)
        for C in Temp.values():
            if Update_Condition(C, P, Unit):
                continue
            if Test_Fun is not None and Test_Fun(C):
                return True
            # Check that the current movement range is not higher...
            if C in Q and M[Q.index(C)] < MovLeft - Dist_Fun(C):
                M[Q.index(C)] = MovLeft - Dist_Fun(C)
            if MovLeft - Dist_Fun(C) >= 0:
                Q.append(C)
                M.append(MovLeft - Dist_Fun(C))
    if Break_Fun is not None:
        return None
    if Test_Fun is not None:
        return False
    return (P)


def Find_Path_To_Nearest_Enemy(Start):
    """
    Finds a path to the nearest enemy, or None if there is no enemy in range.
    :param Start: The Cell to start from.
    :return: A list of Cells with Start at the end of the list, or None if no such path exists.
    """
    Q = [Start]
    P = set()
    LL = {}
    M = [0]
    while len(Q) > 0:
        Ind = M.index(min(M))
        Cell = Q.pop(Ind)
        MovLeft = M.pop(Ind)
        P.add(Cell)
        if DG.tileData[Cell.i, Cell.j].hasUnit and \
                        DG.tileData[Cell.i, Cell.j].unit.P1 != DG.P1Turn:
            break
        Temp = DG.bg.get_neighbors(Cell)
        for C in Temp.values():
            if C is None or C in P:
                continue
            if C in Q:
                if M[Q.index(C)] > MovLeft + C.tile.properties['MovementCost']:
                    M[Q.index(C)] = MovLeft + C.tile.properties['MovementCost']
                    LL[C] = Cell
                continue
            Q.append(C)
            LL[C] = Cell
            M.append(MovLeft + C.tile.properties['MovementCost'])
    # Construct the shortest path.
    Path = [LL[Cell]]
    while Path[-1] != Start:
        try:
            Path.append(LL[Path[-1]])
        except:
            return None
    return Path
