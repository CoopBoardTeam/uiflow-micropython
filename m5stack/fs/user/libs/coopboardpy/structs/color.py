#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>

class Color:
    def __init__(self, r: float=0, g: float=0, b: float=0):
        self.r, self.g, self.b = r, g, b

    def __add__(self, other):
        if isinstance(other, Color):
            return Color(self.r + other.r, self.g + other.g, self.b + other.b)
        else:
            return Color(self.r + other, self.g + other, self.b + other)

    def __mul__(self, other):
        return Color(self.r * other, self.g * other, self.b * other)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.r}, {self.g}, {self.b})'

    def to_tuple(self):
        return self.r, self.g, self.b


if __name__ == '__main__':
    c = Color(10, 10, 10)
    c += 20
    print(c)
