#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>

__all__ = ['event']


class Event:
    def __init__(self):
        self.event_map = {}

    def bind(self, name, function):
        if name not in self.event_map:
            self.event_map[name] = []
        self.event_map[name].append(function)

    def emit(self, name, args):
        if name in self.event_map:
            for function in self.event_map[name]:
                function(args)


event = Event()

