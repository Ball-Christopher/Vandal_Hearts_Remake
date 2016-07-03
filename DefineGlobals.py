# DefineGlobals.py

"""
CHRIS

This file holds variables that need to be shared across files/modules, which is not
particularly easy with Python...

Can be used with import DefineGlobals, with variables called by
DefineGlobals.<Variable Name>

Not partcilarly elegant, but it may be refactored later if it annoys me enough.

02/01/2015: Updated to include control of the director functions...
"""
from cocos.director import director

Scene_Stack = []

class Character():
    def __init__(self, HP, MP, AT, DF, AGL, BaseExp, Class, Move, AtkRng):
        self.HP = HP
        self.MP = MP
        self.AT = AT
        self.DF = DF
        self.AGL = AGL
        self.LVL = BaseExp//100
        self.EXP = BaseExp % 100
        self.Class = Class
        self.Move = Move
        self.AtkRng = AtkRng


    def AddExperience(self, Exp):
        if self.EXP + Exp >= 100:
            self.LVL += (self.EXP + Exp)//100
            self.AddLevel()
        self.EXP = (self.EXP + Exp) % 100

    def AddLevel(self):
        if self.Class == "Hero":
            self.HP += 6
            self.MP += 1
            self.AT += 4
            self.DF += 3
            self.AGL += 3
            pass
        elif self.Class == "Soldier":
            self.HP += 6
            self.AT += 4
            self.DF += 3
            self.AGL += 3
            pass
        elif self.Class == "Archer":
            self.HP += 6
            self.AT += 4
            self.DF += 3
            self.AGL += 3
            pass

def init():
    global scroller, unit_layer, P1Turn, tileData, bg, Ch_Stats
    scroller = None
    unit_layer = None
    P1Turn = None
    tileData = None
    bg = None
    Ch_Stats = {"Ash": Character(42, 5, 30, 29, 23, 500, "Hero", 5, 1),
                "Clint": Character(36, 0, 24, 26, 19, 400, "Soldier", 5, 1),
                "Diego": Character(31, 0, 21, 23, 18, 400, "Archer", 5, 4)}
    pass


def Start():
    # Create a graphics object effectively.
    director.init(resizable=True)  # width=800, height=600, resizable=True)


def AddQueue(main_scene):
    # Run the scene we just created.
    Scene_Stack.append(main_scene)


def Pop():
    try:
        Top = Scene_Stack.pop(0)
        director.run(Top)
    except IndexError:
        pass
