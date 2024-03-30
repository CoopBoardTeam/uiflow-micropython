#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>
from coopboardpy.structs import Key, Color, KeyBoard


class LightManager:
    _named_classes = {}

    @classmethod
    def register(cls, new_class):
        cls._named_classes[new_class.__name__] = new_class
        return cls

    @classmethod
    def support_managers(cls):
        return list(cls._named_classes.keys())

    @classmethod
    def from_dict(cls, d: dict):
        t = d.pop('type')
        return cls._named_classes[t](**d)

    def get_color(self, kb: KeyBoard, dt: float):
        """获得一个键是什么颜色。"""
        raise NotImplementedError()


@LightManager.register
class NoLight(LightManager):
    def get_color(self, kb: KeyBoard, dt: float):
        return [Color() for _ in kb.keys]


if __name__ == '__main__':
    print(LightManager.support_managers())
    print(LightManager.from_dict({'type': 'NoLight'}))

