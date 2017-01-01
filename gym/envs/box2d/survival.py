# import sys
# import math
import time
import uuid
# import numpy as np

import Box2D
import logging

import gym
# from gym import spaces
# from gym.utils import seeding

logger = logging.getLogger(__name__)

VIEWPORT_W = 1600
VIEWPORT_H = 1200

FOOD_SPAWN_RATE = 10
FOOD_LIFETIME = 10


class DeadEntityException(Exception):
    pass


class Entity(object):
    def __init__(self):
        self.lifetime = -1
        self.step_count = 0
        self.id = uuid.uuid4()

    def _render(self, viewer):
        pass

    def _step(self):
        self.step_count += 1

        if self.step_count > self.lifetime:
            raise DeadEntityException


class Food(Entity):
    def __init__(self):
        self.lifetime = FOOD_LIFETIME

    def _step(self):
        Entity._step(self)


class Spawner(object):
    def __init__(self, world):
        self.entities = []
        self.cur_index = 0
        self.world = world

        logger.debug(u"Init Spawner {}".format(self))
    
    def __iter__(self):
        logger.debug(u"Iter {}".format(self))
        self.cur_index = 0
        return self

    def next(self):
        logger.debug(u"Next {}".format(self))
        if self.cur_index >= len(self.entities):
            raise StopIteration
        else:
            ret = self.entities[self.cur_index]
            self.cur_index += 1
            return ret

    def _step(self):
        pass


class SurvivalWorld(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
    }

    def __init__(self):
        self.world = Box2D.b2World()
        self.spawner = Spawner(self.world)

        self._reset()
        self.viewer = None

    def _step(self, action):
        pass

    def _render(self, mode='human', close=False):
        logger.debug(u"Rendering")
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return

        from gym.envs.classic_control import rendering
        if self.viewer is None:
            self.viewer = rendering.Viewer(VIEWPORT_W, VIEWPORT_H)

    def _reset(self):
        self._destroy()

    def _destroy(self):
        pass


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    logger.debug(u"Initializing survival")

    env = SurvivalWorld()
    s = env.reset()

    while True:
        env.step(None)
        env.render()
        time.sleep(1)

    """
    spawn = Spawner()

    assert len(list(iter(spawn))) == 0

    spawn.entities.append(1)

    assert len(list(iter(spawn))) == 1

    spawn.entities.append(2)

    assert len(list(iter(spawn))) == 2
    """
