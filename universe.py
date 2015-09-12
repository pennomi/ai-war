import random
from actions import Move, Shot, Scan
import pyglet
from pyglet import gl
from vec2d import Vec2d

SCAN_DISTANCE = 5
_SCAN_DISTANCE_SQ = SCAN_DISTANCE ** 2


def _velocity_and_direction(ship):
    if ship.direction == Move.UP:
        return Vec2d(0, 1), 0
    elif ship.direction == Move.DOWN:
        return Vec2d(0, -1), 180
    elif ship.direction == Move.RIGHT:
        return Vec2d(1, 0), 90
    elif ship.direction == Move.LEFT:
        return Vec2d(-1, 0), -90


class Universe:
    def __init__(self, size, contender_classes):
        self.size = size
        r = random.randint
        self.ships = []
        for shiptype in contender_classes:
            self.ships += [shiptype(self, Vec2d(r(0, size-1), r(0, size-1)))
                           for _ in range(50)]

    def update(self):
        # execute the move
        for ship in self.ships:
            ship.requested_action = ship.action()
        # direction change requests first!
        for ship in [s for s in self.ships if s.requested_action in Move]:
            ship.direction = ship.requested_action
        # move all ships
        for ship in self.ships:
            self.move_ship(ship)
        # shots
        self.shots = []
        for ship in (s for s in self.ships
                     if isinstance(s.requested_action, Shot)):
            shot = ship.requested_action
            # check that shot is within range
            if self.in_range(shot.owner.position, shot.position):
                self.shots.append(shot)
        # remove all dead ships (only sort of efficiently)
        self.explosions = []  # cause it'll look cool
        for i, ship in enumerate(self.ships):
            for ship2 in self.ships[i+1:] + self.shots:
                if ship.position == ship2.position:
                    ship.dead = True
                    ship2.dead = True
                    self.explosions.append(ship.position)
        [self.ships.remove(ship) for ship in self.ships if ship.dead]
        # scan only if we're not dead
        self.scan_bubbles = []
        for ship in (s for s in self.ships if s.requested_action in Scan):
            ship.received_scan(self.perform_scan(ship))

    def render(self):
        # for smooth rendering
        # draw ships
        for ship in self.ships:
            ship.sprite.position = ship.position * 8 + Vec2d(4, 4)
            ship.sprite.draw()
        gl.glColor3f(1, 1, 0)
        # draw explosions TODO: Animate!
        for explosion in self.explosions:
            gl.glPointSize(8.0)
            pyglet.graphics.draw(
                1, pyglet.gl.GL_POINTS,
                ('v2i', (explosion.x * 8 + 4, explosion.y * 8 + 4))
            )
        laser_points = []
        # draw laser lines
        for shot in self.shots:
            startpos = shot.owner.position * 8 + Vec2d(4, 4)
            laser_points.append(startpos.x)
            laser_points.append(startpos.y)
            laser_points.append(shot.position.x * 8 + 4)
            laser_points.append(shot.position.y * 8 + 4)
        gl.glColor3f(1, 0, 0)
        pyglet.graphics.draw(
            len(self.shots) * 2, pyglet.gl.GL_LINES,
            ('v2i', laser_points)
        )

    def in_range(self, a, b):
        a, b = Vec2d(a), Vec2d(b)  # copy
        # The points wrap around the universe
        if a.x - b.x > self.size / 2:
            b += Vec2d(self.size, 0)
        if a.x - b.x < -self.size / 2:
            b -= Vec2d(self.size, 0)
        if a.y - b.y > self.size / 2:
            b += Vec2d(0, self.size)
        if a.y - b.y < -self.size / 2:
            b -= Vec2d(0, self.size)
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= _SCAN_DISTANCE_SQ

    def move_ship(self, ship):
        velocity, direction = _velocity_and_direction(ship)
        ship.position += velocity
        ship.sprite.rotation = direction
        ship.position %= self.size

    def perform_scan(self, ship):
        """Return the position and broadcast data of all ships in range."""
        scan_data = []
        for s in self.ships:
            if self.in_range(s.position, ship.position) and not s is ship:
                scan_data.append((s.position, s.broadcast()))

        # If we want to render the scanners, we'll need to render them
        centers = [
            ship.position,
            ship.position + Vec2d(self.size, 0),
            ship.position + Vec2d(0, self.size),
            ship.position + Vec2d(self.size, self.size),
            ship.position + Vec2d(-self.size, 0),
            ship.position + Vec2d(0, -self.size),
            ship.position + Vec2d(-self.size, -self.size),
        ]
        self.scan_bubbles.extend(centers)

        return scan_data