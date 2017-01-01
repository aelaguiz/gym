# import sys
# import math
import time
import uuid
import random
# import numpy as np

import Box2D
import logging

import gym
# from gym import spaces
# from gym.utils import seeding

logger = logging.getLogger(__name__)

VIEWPORT_W = 1600
VIEWPORT_H = 1200

FOOD_SPAWN_RATE = 10  # 1 tick in 100
FOOD_LIFETIME = 10


class DeadEntityException(Exception):
    pass


class Entity(object):
    def __init__(self, entity_type):
        self.lifetime = -1
        self.step_count = 0
        self.id = uuid.uuid4()
        self.entity_type = entity_type

        logger.debug(u"Spawned new entity {}".format(self))

    def __repr__(self):
        return u"Entity {} id: {}".format(self.entity_type, self.id)

    def _render(self, viewer):
        pass

    def _step(self):
        self.step_count += 1

        if self.lifetime > 0 and self.step_count > self.lifetime:
            raise DeadEntityException


class Food(Entity):
    def __init__(self):
        Entity.__init__(self, "food")

        self.lifetime = FOOD_LIFETIME


class Spawner(object):
    def __init__(self, world):
        self.entities = []
        self.cur_index = 0
        self.world = world

        logger.debug(u"Init Spawner {}".format(self))
    
    def __iter__(self):
        self.cur_index = 0
        return self

    def next(self):
        if self.cur_index >= len(self.entities):
            raise StopIteration
        else:
            ret = self.entities[self.cur_index]
            self.cur_index += 1
            return ret

    def _step(self):
        logger.debug(u"Stepping spawner")
        if random.randint(0, FOOD_SPAWN_RATE) == 0:
            self._spawn_food()

        new_list = []

        logger.debug(u"Stepping {} entities".format(len(self.entities)))

        for entity in self.entities:
            try:
                entity._step()

                new_list.append(entity)
            except DeadEntityException:
                logger.debug(u"Entity dead {}".format(entity))

        self.entities = new_list

    def _spawn_food(self):
        new_entity = Food()
        self._spawn_entity(new_entity)

    def _spawn_entity(self, new_entity):
        self.entities.append(new_entity)


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
        self.spawner._step()
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
        env._step(None)
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
