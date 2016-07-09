import cocos

# Import menu classes
from cocos.menu import Menu,MenuItem, fixedPositionMenuLayout
from Utilities import Resolve_Attack
'''
CHRIS

This class controls the user interaction with the game, such as
what should happen when the user clicks a button.  Defines a whole
set of context menus (which should probably be separated out) and
dispatchs the events to the relevant Units class.

To Do:
"End Turn" menu
Proper victory transitions
More than two sides???
'''
import DefineGlobals

class MouseDisplay(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super( MouseDisplay, self).__init__()

        self.position = (100,240)
        self.last = (-1,-1)
        self.InMenu = False
        self.Attack = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.position = (x,y)
        mx, my = DefineGlobals.scroller.pixel_from_screen(x, y)
        cell = DefineGlobals.bg.get_at_pixel(mx, my)
        key = DefineGlobals.bg.get_key_at_pixel(mx, my)
        New_Tile = DefineGlobals.tileData[key]
        # Check that user clicked inside the map, and inside any context menus.
        if not cell or self.InMenu:
            return
        # Check that the user is not attacking
        if self.Attack and 'color4' in cell.properties.keys() and \
                        cell.properties['color4'] == (255,0,0,255) and \
                New_Tile.hasUnit and New_Tile.unit.P1 != DefineGlobals.P1Turn:
            Resolve_Attack(self.last, key)
            self.Attack = False
            self.RemoveHighlight()
            self.UpdateTurn(DefineGlobals.P1Turn)
            # Check the victory conditions
            P1_Alive = False
            P2_Alive = False
            for T in DefineGlobals.tileData.values():
                if T.hasUnit and T.unit.P1:
                    P1_Alive = True
                if T.hasUnit and not T.unit.P1:
                    P2_Alive = True
                if P1_Alive and P2_Alive: return
            # DO something about the victory conditions
            print("Player 1 Wins" if P1_Alive else "Player 2 Wins")
            DefineGlobals.Pop()
        elif self.Attack:
            return
        # Check if user can move the unit (by looking at the tile color)
        if 'color4' in cell.properties.keys() and cell.properties['color4'] == (0, 0, 255, 255):
            # Move the unit to this square.
            Old_Tile = DefineGlobals.tileData[self.last]
            NewCell = DefineGlobals.bg.get_key_at_pixel(mx, my)
            if Old_Tile.unit.P1 == DefineGlobals.P1Turn and \
                    (New_Tile == Old_Tile or not DefineGlobals.tileData[NewCell].hasUnit):
                Old_Tile.unit.MoveUnit(NewCell[0] - self.last[0], NewCell[1] - self.last[1])
                self.ActionMenu(DefineGlobals.tileData[NewCell], self.last)
            self.last = DefineGlobals.bg.get_key_at_pixel(mx, my)
            self.RemoveHighlight()
            return
        self.RemoveHighlight()
        # If we have clicked on a unit, highlight the available movement squares.
        if New_Tile.hasUnit and New_Tile.unit.P1 == DefineGlobals.P1Turn:  # CHECK FOR MOVEMENT AND CORRECT TEAM TOO.
            New_Tile.unit.HighlightAvailable()
            self.last = DefineGlobals.bg.get_key_at_pixel(mx, my)
            return
        # Finally, if we click on an empty square we want to bring up a "End Turn" menu

    def ActionMenu(self, T, last):
        # Set flag so that only operations within the menu can be performed.
        self.InMenu = True
        # Create a "Sprite" which is the menu background.
        self.contextMenuBck = cocos.sprite.Sprite('Resources/popup_bg.png')
        # Create a list of menu items
        l = []
        # Check if the unit can attack, if so add a menu item.
        Unit = T.unit
        if Unit.HighlightAttack(True):
            MI_Attack = MenuItem('Attack', lambda: self.MAttack(T))
            l.append(MI_Attack)
        MI_Stay = MenuItem('Stay', self.Stay)
        MI_Cancel = MenuItem('Cancel', lambda: self.Cancel(T,last))
        l.extend( [MI_Stay, MI_Cancel])
        # Create a menu container.
        self.M = Menu()
        self.M.font_item['color'] = (0, 0, 0, 255)
        self.M.font_item['font_size'] = 12
        self.M.font_item_selected['color'] = (0, 0, 0, 255)
        self.M.font_item_selected['font_size'] = 15
        self.M.font_item_selected['bold'] = True
        # Optimally space the menu given the number of items
        Top = self.contextMenuBck.get_rect().get_top()
        Bot = self.contextMenuBck.get_rect().get_bottom()
        Mid = (Top-Bot)//2
        MenuItemPositions = [(0,Mid-((i+1)*2*Mid)//(len(l)+1)) for i in range(len(l))]
        # Create the menu from the list of menu items.  Fixed Position allows
        # us to specify everything relative to the center of the menu sprite.
        self.M.create_menu(l, layout_strategy=fixedPositionMenuLayout(
                            MenuItemPositions))
        # Add the menu to the background.
        self.contextMenuBck.add(self.M)
        # Find the units position
        Unit = T.unit
        Pos = Unit.Sprite.position
        # Put the menu in the correct place...
        if Pos[0] <= DefineGlobals.bg.px_width//2 and Pos[1] <= DefineGlobals.bg.px_height//2:
            # Put menu above right
            self.contextMenuBck.position = (Pos[0]+50,Pos[1]+50)
        elif Pos[0] > DefineGlobals.bg.px_width//2 and Pos[1] <= DefineGlobals.bg.px_height//2:
            # Put menu above left
            self.contextMenuBck.position = (Pos[0]-50,Pos[1]+50)
        elif Pos[0] <= DefineGlobals.bg.px_width//2 and Pos[1] > DefineGlobals.bg.px_height//2:
            # Put menu below right
            self.contextMenuBck.position = (Pos[0]+50,Pos[1]-50)
        else:
            # Put menu below left
            self.contextMenuBck.position = (Pos[0]-50,Pos[1]-50)
        # Place the anchor for the menu at the same place as the background.
        self.M.anchor = self.contextMenuBck.anchor
        self.M.position = (0,0)
        # Add the menu to the unit layer.
        DefineGlobals.unit_layer.add(self.contextMenuBck)

    def Stay(self):
        self.InMenu = False
        DefineGlobals.unit_layer.remove(self.contextMenuBck)
        self.UpdateTurn(DefineGlobals.P1Turn)
        pass

    def Cancel(self,T,last):
        self.InMenu = False
        CP = DefineGlobals.bg.get_key_at_pixel(T.unit.Sprite.position[0], T.unit.Sprite.position[1])
        T.unit.MoveUnit(last[0] - CP[0], last[1] - CP[1], Unmove=True)
        DefineGlobals.unit_layer.remove(self.contextMenuBck)
        pass

    def MAttack(self, T):
        ''' Not implmented yet... '''
        self.InMenu = False
        self.Attack = True
        Unit = T.unit
        Unit.HighlightAttack()
        DefineGlobals.unit_layer.remove(self.contextMenuBck)
        pass

    def RemoveHighlight(self):
        # Remove all highlighting from the map...
        for col in DefineGlobals.bg.cells:
            for c in col:
                DefineGlobals.bg.set_cell_color(c.i, c.j, (255, 255, 255))
                DefineGlobals.bg.set_cell_opacity(c.i, c.j, 255)

    def UpdateTurn(self,PTurn):
        # Check if all units in the current turn have moved
        # This is ugly, but it works...
        for T in DefineGlobals.tileData.values():
            if T.hasUnit and T.unit.P1 == PTurn and T.unit.moved == False:
                # If there is a unit that hasn't moved on the moving side don't change.
                return
        # Else change turn if everyone has moved.
        for T in DefineGlobals.tileData.values():
            if T.hasUnit and T.unit.P1 == PTurn:
                T.unit.EndTurn()
        DefineGlobals.P1Turn = not DefineGlobals.P1Turn
        # Add the "AI" layer over the top.
        if not DefineGlobals.P1Turn:
            Units = [New_Tile.unit for New_Tile in DefineGlobals.tileData.values()
                     if New_Tile.hasUnit and New_Tile.unit.P1 == DefineGlobals.P1Turn]
            for Enemy in Units:
                Enemy.Zombie()
                Enemy.EndTurn()
        DefineGlobals.P1Turn = not DefineGlobals.P1Turn
