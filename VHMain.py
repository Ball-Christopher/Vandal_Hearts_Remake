import pyglet

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

# Additional imports
from Control import Control

import DG

DG.init()

'''
CHRIS

Implemented:
Background map correctly displays, is slow however.
Tile information is extracted, position, movement cost, type.
Create and display units correctly. CONCERN!
Units cannot move through enemies.
Units cannot move to an occupied space.
Remove highlighting from squares with enemies on for flying units?
Generate health points for units.
Allow attacking, remove units when defeated.
Add Zombie AI (Attack random enemy in range, else do nothing).
Add Zombie AI (go towards nearest and attack).

Stack:
Add direction (+ bonuses for attacking/defending)
Add class (+bonuses for attacking/defending)
Add terrain (+bonuses for attacking/defending)
Add victory scene
Add magic
Refactor menu code to avoid extremely long methods.
Animate movement.
Indicator on screen for whose turn it is.
Indicator for moved/unmoved units.
'''

if __name__ == '__main__':
    A = Control()
    #A.main()
    pass
