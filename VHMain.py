import pyglet
from pyglet.window import key,mouse

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

# Additional imports
from Control import Control

import DefineGlobals

DefineGlobals.init()

'''
CHRIS

Implemented:
Background map correctly displays, is slow however.
Tile information is extracted, position, movement cost, type.
Create and display units correctly. CONCERN!
Units cannot move through enemies.
Units cannot move to an occupied space.
Remove highlighting from squares with enemies on for flying units?

Stack:
Fix upside down location from Tiled...
Fix invisible mountain backdrop.  Conflict with file in folder???
Generate health points for units.
Allow attacking, remove units when defeated.
Animate movement.
Indicator on screen for whose turn it is.
Indicator for moved/unmoved units.
'''

if __name__ == '__main__':
    A = Control()
    #A.main()
    pass
