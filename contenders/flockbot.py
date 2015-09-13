import uuid
import hashlib
from actions import Move, Shot, Scan
from ship import Ship
from vec2d import Vec2d


secret = str(uuid.uuid4())


class FlockBot(Ship):
    lined_up = False
    positioned = False
    strategy = 'init'
    counter = 0
    uid_generator = 45
    code = ''
    scan_data = {
        'counter': counter,
        'friends': [],
        'enemies': []
    }

    def __new__(cls, *args, **kwargs):
        cls.uid_generator += 1
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super(FlockBot, self).__init__(*args, **kwargs)
        self.uid = self.uid_generator

    def action(self):
        self.counter += 1
        crypt_str = (secret + str(self.counter)).encode('utf-8')
        self.code = hashlib.md5(crypt_str).hexdigest()

        if self.counter < 200:
            if self.position.x != self.uid:
                if self.position.x > self.uid:
                    return Move.LEFT
                else:
                    return Move.RIGHT
            if self.lined_up:
                return self.shoot_enemies()
            if self.position.y > 2:
                return self.rendezvous()
            if self.counter < 100:
                return self.idle()
        if self.direction != Move.UP:
            return Move.UP
        if not self.counter % 20:
            return Move.RIGHT
        return self.shoot_enemies()

    def synced(self):
        return (self.position.y % 2) == (self.counter % 2)

    def rendezvous(self):
        # go to the bottom while scanning and shooting enemies
        if self.position.y > 50:
            if self.direction != Move.UP:
                return Move.UP
        elif self.direction != Move.DOWN:
            return Move.DOWN
        return self.shoot_enemies()

    def idle(self):
        # stay under y=5, scanning for enemies and shooting at them until the
        # line is formed
        if self.position.y == 0:
            return Move.UP
        elif self.position.y == 1:
            return Move.DOWN
        # if not self.synced():
        #     if self.direction == Move.UP:
        #         return Move.DOWN
        #     return Move.UP
        # return self.shoot_enemies()

    def shoot_enemies(self):
        return Shot(self.position + Vec2d(0, 10), self)

    def received_scan(self, discovered_objects):
        self.scan_data['counter'] = self.counter
        friends = []
        enemies = []
        for position, data in discovered_objects:
            if data != self.code:
                enemies.append(position)
            else:
                friends.append(position)
        self.scan_data['friends'] = friends
        self.scan_data['enemies'] = enemies

    def broadcast(self):
        return self.code
