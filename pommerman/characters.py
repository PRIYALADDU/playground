"""These are objects in the game world. Please do not edit this file. The competition will be run with it as is."""

import random

from .envs import utility


class Bomber(object):
    """Container to keep the agent state."""

    def __init__(self, agent_id=None, game_type=None):
        self._game_type = game_type
        self.ammo = 1
        self.is_alive = True
        self.blast_strength = utility.DEFAULT_BLAST_STRENGTH
        self.can_kick = False
        if agent_id is not None:
            self.set_agent_id(agent_id)

    def set_agent_id(self, agent_id):
        self.agent_id = agent_id
        if self._game_type == utility.GameType.FFA:
            self.teammate = utility.Item.AgentDummy
            self.enemies = [getattr(utility.Item, 'Agent%d' % id_)
                            for id_ in range(4) if id_ != agent_id]
        else:
            teammate_id = (agent_id + 2) % 4
            self.teammate = getattr(utility.Item, 'Agent%d' % teammate_id)
            self.enemies = [getattr(utility.Item, 'Agent%d' % id_)
                            for id_ in range(4) if id_ != agent_id and id_ != teammate_id]
            self.enemies.append(utility.Item.AgentDummy)

    def maybe_lay_bomb(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bomb(self, self.position, utility.DEFAULT_BOMB_LIFE, self.blast_strength)
        return None

    def incr_ammo(self):
        self.ammo += 1

    def get_next_position(self, direction):
        action = utility.Action(direction)
        return utility.get_next_position(self.position, action)

    def move(self, direction):
        self.position = self.get_next_position(direction)

    def stop(self):
        pass

    def in_range(self, exploded_map):
        row, col = self.position
        return exploded_map[row][col] == 1

    def die(self):
        self.is_alive = False

    def set_start_position(self, start_position):
        self.start_position = start_position

    def reset(self, ammo=1, is_alive=True, blast_strength=None, can_kick=False):
        self.position = self.start_position
        self.ammo = ammo
        self.is_alive = is_alive
        self.blast_strength = blast_strength or utility.DEFAULT_BLAST_STRENGTH
        self.can_kick = can_kick

    def pick_up(self, item):
        if item == utility.Item.ExtraBomb:
            self.ammo = min(self.ammo + 1, 10)
        elif item == utility.Item.IncrRange:
            self.blast_strength = min(self.blast_strength + 1, 10)
        elif item == utility.Item.Kick:
            self.can_kick = True
        elif item == utility.Item.Skull:
            rand = random.random()
            if rand < .33:
                self.blast_strength = max(2, self.blast_strength - 1)
            elif rand < .66:
                self.ammo = max(1, self.ammo - 1)
            else:
                self.blast_strength += 2
                self.blast_strength = min(self.blast_strength, 10)

    def to_json(self):
        return {
            "agent_id": self.agent_id,
            "is_alive": self.is_alive,
            "position": self.position,
            "ammo": self.ammo,
            "blast_strength": self.blast_strength,
            "can_kick": self.can_kick
        }


class Bomb(object):
    """Container for the Bomb object."""

    def __init__(self, bomber, position, life, blast_strength, moving_direction=None):
        self.bomber = bomber
        self.position = position
        self.life = life
        self.blast_strength = blast_strength
        self.moving_direction = moving_direction

    def tick(self):
        self.life -= 1

    def move(self):
        if self.is_moving():
            self.position = utility.get_next_position(self.position, self.moving_direction)

    def stop(self):
        self.moving_direction = None

    def exploded(self):
        return self.life == 0

    def explode(self):
        row, col = self.position
        indices = {
            'up': ([row - i, col] for i in range(1, self.blast_strength)),
            'down': ([row + i, col] for i in range(self.blast_strength)),
            'left': ([row, col - i] for i in range(1, self.blast_strength)),
            'right': ([row, col + i] for i in range(1, self.blast_strength))
        }
        return indices

    def in_range(self, exploded_map):
        row, col = self.position
        return exploded_map[row][col] == 1

    def is_moving(self):
        return self.moving_direction is not None

    def to_json(self):
        return {
            "position": self.position,
            "bomber_id": self.bomber.agent_id,
            "life": self.life,
            "blast_strength": self.blast_strength,
            "moving_direction": self.moving_direction
        }


class Flame(object):
    """Container for Flame object."""

    def __init__(self, position, life=2):
        self.position = position
        self._life = life

    def tick(self):
        self._life -= 1

    def is_dead(self):
        return self._life == 0

    def to_json(self):
        return {
            "position": self.position,
            "life": self._life
        }

