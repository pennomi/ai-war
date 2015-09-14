from enum import Enum


class Move(Enum):
    """Return a move if you want to change the direction you're moving."""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Scan(Enum):
    """Return Scan.SCAN if you want to see what's around your ship."""
    SCAN = 1


class Shot:
    """A returned Shot instance targets a point you want to exterminate."""
    def __init__(self, position, owner):
        self.position = position
        self.owner = owner
