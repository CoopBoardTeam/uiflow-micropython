#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>

"""
灯效果动画。此文件不会自动加载，如果需要则需要手动在__init__.py中引入。
"""
import math

from coopboardpy.driver import driver
from coopboardpy.event import event
from coopboardpy.light.base import LightManager
from coopboardpy.structs import KeyBoard, Color


@LightManager.register
class Sin(LightManager):
    def __init__(self, kx=0.5, ky=1, speed=0.05, xy_rotation=True):
        self.kx = kx
        self.ky = ky
        self.speed = speed
        self.t = 0
        self.xy_rotation = xy_rotation

    def _sin0_1(self, d):
        return (math.sin(d) + 1.) / 2

    def get_color(self, kb: KeyBoard, dt: float):
        """获得一个键是什么颜色。"""
        self.t += dt * self.speed
        if self.t > 2 * math.pi:
            self.t -= 2 * math.pi
        ret = []
        for k in kb.keys:
            d = (k.x * self.kx * math.sin(self.t) + k.y * self.ky * math.cos(self.t)) + self.t
            ret.append(Color(self._sin0_1(d - math.pi * 2 / 3), self._sin0_1(d), self._sin0_1(d + math.pi * 2 / 3)))
        return ret


class LineRunState:
    def __init__(self, c: Color, s: float):
        self.c = c
        self.s = s


@LightManager.register
class LineRun(LightManager):
    def __init__(self, width=6, speed=2., sparse=20):
        self.row = []
        self.width = width
        self.speed = speed
        self.max_x = 0
        self.sparse = sparse  # 稀疏，越大越稀疏

    def new_state(self) -> LineRunState:
        c = Color(*(driver.random() * 0.4 + 0.6 for _ in range(3)))
        return LineRunState(c, -self.sparse * driver.random())

    def get_color(self, kb: KeyBoard, dt: float):
        if not self.max_x:  # init
            self.max_x = max(k.x for k in kb.keys)
            max_row = max(k.r for k in kb.keys)
            self.row = [self.new_state() for _ in range(max_row + 1)]
        for vid, v in enumerate(self.row):
            v.s += self.speed * dt
            if v.s > self.max_x + self.width:
                self.row[vid] = self.new_state()
        ret = []
        for k in kb.keys:
            r = (k.x - (self.row[k.r].s - self.width)) / self.width
            ret.append(self.row[k.r].c * r if 0 < r <= 1 else Color())
        return ret


@LightManager.register
class Switch(LightManager):
    def __init__(self, managers: 'List[Union[dict, LightManager]]'):
        self.managers = [(m if isinstance(m, LightManager) else LightManager.from_dict(m)) for m in managers]
        self.cur_id = 0
        event.bind('next_light', self.next_light)
        event.bind('prev_light', self.prev_light)

    def next_light(self, args):
        self.cur_id = (self.cur_id + 1) % len(self.managers)

    def prev_light(self, args):
        self.cur_id = (self.cur_id - 1 + len(self.managers)) % len(self.managers)

    def get_color(self, kb: KeyBoard, dt: float):
        return self.managers[self.cur_id].get_color(kb, dt)


