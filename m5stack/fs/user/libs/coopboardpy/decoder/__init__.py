#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Liu Yang <mkliuyang@gmail.com>
"""
将检测到的按键（按键id组合）解码为可发送的按键编码
"""
from .base import Decoder


def get_decoder(cfg):
    from .base import SimpleDecoder, AutoFitDecoder
    return AutoFitDecoder(cfg)

