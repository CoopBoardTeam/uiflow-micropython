#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>
from coopboardpy.structs import Color


class CoopBoardDriver:
    """键盘python驱动，统一接口功能如下。用户需要继承并实现对应的接口。
        1. 按键状态扫描
        2. 按键码输出
        3. 灯光输出
    """
    def start(self, cfg):
        """启动钩子。在运行功能前调用的钩子"""
        pass

    def close(self, cfg):
        """结束钩子。停止运行"""
        pass

    # 下面是供给逻辑调用的底层函数。
    def scan_key(self) -> 'List[int]':
        return []

    def send_keycode(self, codes: 'List[SendCode]') -> None:
        pass

    def set_light(self, lights: 'List[Color]') -> None:
        pass

    def wait_us(self, n: int) -> None:
        raise NotImplementedError()

    def log(self, msg: str, level='info') -> None:
        pass

    def random(self) -> float:
        raise NotImplementedError()

