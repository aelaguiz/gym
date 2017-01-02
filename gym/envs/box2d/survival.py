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
from gym.envs.classic_control import rendering

logger = logging.getLogger(__name__)

VIEWPORT_W = 400
VIEWPORT_H = 600

FOOD_SPAWN_RATE = 2
FOOD_LIFETIME = 2
FOOD_RADIUS = 20

SHARK_SPAWN_RATE = 2
SHARK_LIFETIME = -1


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

    def render(self, viewer):
        pass

    def step(self):
        self.step_count += 1

        if self.lifetime > 0 and self.step_count > self.lifetime:
            raise DeadEntityException


class Food(Entity):
    def __init__(self, world):
        Entity.__init__(self, "food")

        self.lifetime = FOOD_LIFETIME

        x = random.randint(0, VIEWPORT_W)
        y = random.randint(0, VIEWPORT_H)

        self.body = world.CreateDynamicBody(
            position=(x, y),
            angle=0.0,
            fixtures=Box2D.b2.fixtureDef(
                shape=Box2D.b2.circleShape(
                    radius=FOOD_RADIUS
                )
            )
        )

    def render(self, viewer):
        f = self.body.fixtures[0]
        trans = self.body.transform
        t = rendering.Transform(translation=trans * f.shape.pos)
        viewer.draw_circle(
            FOOD_RADIUS,
            color=(1, 0, 0)
        ).add_attr(t)


class Shark(Entity):
    def __init__(self, world):
        Entity.__init__(self, "shark")

        self.lifetime = SHARK_LIFETIME

        x = random.randint(0, VIEWPORT_W)
        y = random.randint(0, VIEWPORT_H)

        self.body = world.CreateDynamicBody(
            position=(x, y),
            angle=0.0,
            fixtures=Box2D.b2.fixtureDef(
                shape=Box2D.b2.polygonShape(
                    vertices=[
                        (-15, 0),
                        (0, 15),
                        (15, 0),
                        (15, -15),
                        (-15, -15)
                    ]
                )
            )
        )

    def render(self, viewer):
        f = self.body.fixtures[0]
        trans = self.body.transform

        path = [trans * v for v in f.shape.vertices]
        viewer.draw_polygon(
            path,
            color=(0, 0, 1)
        )


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

        if random.randint(0, SHARK_SPAWN_RATE) == 0:
            self._spawn_shark()

        new_list = []

        logger.debug(u"Stepping {} entities".format(len(self.entities)))

        for entity in self.entities:
            try:
                entity.step()

                new_list.append(entity)
            except DeadEntityException:
                logger.debug(u"Entity dead {}".format(entity))

        self.entities = new_list

    def _spawn_food(self):
        new_entity = Food(self.world)
        self._spawn_entity(new_entity)

    def _spawn_shark(self):
        new_entity = Shark(self.world)
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

        if self.viewer is None:
            self.viewer = rendering.Viewer(VIEWPORT_W, VIEWPORT_H)

        for entity in self.spawner:
            entity.render(self.viewer)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

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
