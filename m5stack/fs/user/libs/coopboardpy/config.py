#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>

"""硬件配置，规定了使用那种硬件，哪种按键配置。"""
from coopboardpy.structs import KeyBoard, CodeMap
from coopboardpy.light import LightManager


class Cfg:
    def __init__(self, platform=None, keyboard=None, code_map=None, light=None):
        self.platform: str = platform
        self.keyboard: KeyBoard = keyboard
        self.code_map: CodeMap = code_map
        self.light: LightManager = light

    def reload_from_dict(self, d):
        self.platform = d['platform']
        self.keyboard = KeyBoard.from_quick_set(d['keyboard'])
        self.code_map = CodeMap.from_dict(d['code'])
        self.light = LightManager.from_dict(d['light'])

    @classmethod
    def from_dict(cls, d):
        o = cls()
        o.reload_from_dict(d)
        return o




